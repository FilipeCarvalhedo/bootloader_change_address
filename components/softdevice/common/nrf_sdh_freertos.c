/**
 * Copyright (c) 2017 - 2022, Nordic Semiconductor ASA
 *
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this
 *    list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form, except as embedded into a Nordic
 *    Semiconductor ASA integrated circuit in a product or a software update for
 *    such product, must reproduce the above copyright notice, this list of
 *    conditions and the following disclaimer in the documentation and/or other
 *    materials provided with the distribution.
 *
 * 3. Neither the name of Nordic Semiconductor ASA nor the names of its
 *    contributors may be used to endorse or promote products derived from this
 *    software without specific prior written permission.
 *
 * 4. This software, with or without modification, must only be used with a
 *    Nordic Semiconductor ASA integrated circuit.
 *
 * 5. Any software provided in binary form under this license must not be reverse
 *    engineered, decompiled, modified and/or disassembled.
 *
 * THIS SOFTWARE IS PROVIDED BY NORDIC SEMICONDUCTOR ASA "AS IS" AND ANY EXPRESS
 * OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY, NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL NORDIC SEMICONDUCTOR ASA OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
 * GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */

#include "nrf_sdh_freertos.h"
#include "nrf_sdh.h"

/* Group of FreeRTOS-related includes. */
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "semphr.h"

#define NRF_LOG_MODULE_NAME nrf_sdh_freertos
#include "nrf_log.h"
NRF_LOG_MODULE_REGISTER();

#define NRF_BLE_FREERTOS_SDH_TASK_STACK 256


static TaskHandle_t                 m_softdevice_task;  //!< Reference to SoftDevice FreeRTOS task.
static nrf_sdh_freertos_task_hook_t m_task_hook;        //!< A hook function run by the SoftDevice task before entering its loop.

#if defined(MBS_INTEGRATION) && NRF_MODULE_ENABLED(NRF_SDH_SOC)
#include "sdk_common.h"
#include "nrf_sdh_soc.h"
#include "nrf_soc.h"
#include "app_error.h"

NRF_SECTION_SET_DEF(sdh_soc_observers, nrf_sdh_soc_evt_observer_t, NRF_SDH_SOC_OBSERVER_PRIO_LEVELS);

static void nrf_sdh_soc_evts_poll(void)
{
    ret_code_t ret_code;

    while (true)
    {
        uint32_t evt_id;

        ret_code = sd_evt_get(&evt_id);
        if (ret_code != NRF_SUCCESS)
        {
            break;
        }

        NRF_LOG_DEBUG("SoC event: 0x%x.", evt_id);

        // Forward the event to SoC observers.
        nrf_section_iter_t  iter;
        for (nrf_section_iter_init(&iter, &sdh_soc_observers);
             nrf_section_iter_get(&iter) != NULL;
             nrf_section_iter_next(&iter))
        {
            nrf_sdh_soc_evt_observer_t * p_observer;
            nrf_sdh_soc_evt_handler_t    handler;

            p_observer = (nrf_sdh_soc_evt_observer_t *) nrf_section_iter_get(&iter);
            handler    = p_observer->handler;

            handler(evt_id, p_observer->p_context);
        }
    }

    if (ret_code != NRF_ERROR_NOT_FOUND)
    {
        APP_ERROR_HANDLER(ret_code);
    }
}
#endif // defined(MBS_INTEGRATION) && NRF_MODULE_ENABLED(NRF_SDH_SOC)

void SD_EVT_IRQHandler(void)
{
#if defined(MBS_INTEGRATION) && NRF_MODULE_ENABLED(NRF_SDH_SOC)
    /**
     * Process NRF_SOC_EVTS in the interrupt handler.
     * We wish to have blocking internal flash memory operations even if called from a ble event
     * handler/observer in the softdevice task but the result events of such operations are propagated
     * from the softdevice which would be processed in the same blocking task context leading to deadlock
     * if not processed directly in the interrupt handler.
     */
     nrf_sdh_soc_evts_poll();
#endif

    BaseType_t yield_req = pdFALSE;


    vTaskNotifyGiveFromISR(m_softdevice_task, &yield_req);

    /* Switch the task if required. */
    portYIELD_FROM_ISR(yield_req);
}


/* This function gets events from the SoftDevice and processes them. */
static void softdevice_task(void * pvParameter)
{
    NRF_LOG_DEBUG("Enter softdevice_task.");

    if (m_task_hook != NULL)
    {
        m_task_hook(pvParameter);
    }

    while (true)
    {
        nrf_sdh_evts_poll();                    /* let the handlers run first, incase the EVENT occured before creating this task */

        (void) ulTaskNotifyTake(pdTRUE,         /* Clear the notification value before exiting (equivalent to the binary semaphore). */
                                portMAX_DELAY); /* Block indefinitely (INCLUDE_vTaskSuspend has to be enabled).*/
    }
}


void nrf_sdh_freertos_init(nrf_sdh_freertos_task_hook_t hook_fn, void * p_context)
{
    NRF_LOG_DEBUG("Creating a SoftDevice task.");

    m_task_hook = hook_fn;

#if defined(MBS_INTEGRATION) && defined(BLE_SOFTDEVICE_TASK_STACK_SIZE)
    BaseType_t xReturned = xTaskCreate(softdevice_task,
                                       "BLE softdevice",
                                       BLE_SOFTDEVICE_TASK_STACK_SIZE,
                                       p_context,
                                       BLE_SOFTDEVICE_TASK_PRIO,
                                       &m_softdevice_task);
#else
    BaseType_t xReturned = xTaskCreate(softdevice_task,
                                       "BLE",
                                       NRF_BLE_FREERTOS_SDH_TASK_STACK,
                                       p_context,
                                       2,
                                       &m_softdevice_task);
#pragma message "Default values for softdevice task used! Change by defining BLE_SOFTDEVICE_TASK_STACK_SIZE and BLE_SOFTDEVICE_TASK_PRIO in your product"
#endif
    if (xReturned != pdPASS)
    {
        NRF_LOG_ERROR("SoftDevice task not created.");
        APP_ERROR_HANDLER(NRF_ERROR_NO_MEM);
    }
}
