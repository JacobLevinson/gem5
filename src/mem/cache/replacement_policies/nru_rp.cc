/**
 * Copyright (c) 2018-2020 Inria
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met: redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer;
 * redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution;
 * neither the name of the copyright holders nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include "mem/cache/replacement_policies/nru_rp.hh"

#include <cassert>
#include <memory>

#include "params/NRURP.hh"
#include "sim/cur_tick.hh"

namespace gem5
{

    namespace replacement_policy
    {

        NRU::NRU(const Params &p)
            : Base(p)
        {
        }

        void
        NRU::invalidate(const std::shared_ptr<ReplacementData> &replacement_data)
        {
            auto repl_data = std::static_pointer_cast<NRUReplData>(replacement_data);
            // Reset to not recently used (ready for eviction)
            repl_data->nru = true;
            // Mark entry as invalid
            repl_data->valid = false;
        }

        void
        NRU::touch(const std::shared_ptr<ReplacementData> &replacement_data) const
        {
            // Update it is recently used
            std::static_pointer_cast<NRUReplData>(
                replacement_data)
                ->nru = false;
        }

        void
        NRU::reset(const std::shared_ptr<ReplacementData> &replacement_data) const
        {
            auto repl_data = std::static_pointer_cast<NRUReplData>(replacement_data);
            // Set as recently used
            repl_data->nru = false;
            // Mark entry as valid
            repl_data->valid = true;
        }

        ReplaceableEntry *
        NRU::getVictim(const ReplacementCandidates &candidates) const
        {
            // There must be at least one replacement candidate
            assert(candidates.size() > 0);

            // First look for an invalid entry
            for (const auto &candidate : candidates)
            {
                if (!std::static_pointer_cast<NRUReplData>(
                         candidate->replacementData)
                         ->valid)
                {
                    return candidate;
                }
            }

            // If no invalid entry is found, we must evict a valid one


            // Go through once to see if any are nru
            for (const auto &candidate : candidates)
            {
                if (std::static_pointer_cast<NRUReplData>(
                        candidate->replacementData)
                        ->nru)
                {
                    return candidate;
                }
            }    

            // If no nru entries are found, reset all entries to nru
            for (const auto &candidate : candidates)
            {
                std::static_pointer_cast<NRUReplData>(
                    candidate->replacementData)
                    ->nru = true;
            }

            return candidates[0]; // Return the leftmost entry (its now nru)
        }

        std::shared_ptr<ReplacementData>
        NRU::instantiateEntry()
        {
            return std::shared_ptr<ReplacementData>(new NRUReplData());
        }

    } // namespace replacement_policy
} // namespace gem5
