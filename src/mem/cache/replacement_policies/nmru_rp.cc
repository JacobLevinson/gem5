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

#include "mem/cache/replacement_policies/nmru_rp.hh"

#include <cassert>
#include <memory>

#include "params/NMRURP.hh"
#include "sim/cur_tick.hh"

namespace gem5
{

    namespace replacement_policy
    {

        NMRU::NMRU(const Params &p)
            : Base(p)
        {
        }

        void
        NMRU::invalidate(const std::shared_ptr<ReplacementData> &replacement_data)
        {
            auto repl_data = std::static_pointer_cast<NMRUReplData>(replacement_data);
            // Reset last touch timestamp
            repl_data->lastTouchTick = Tick(0);
            // Mark entry as invalid
            repl_data->valid = false;
        }

        void
        NMRU::touch(const std::shared_ptr<ReplacementData> &replacement_data) const
        {
            // Update last touch timestamp
            std::static_pointer_cast<NMRUReplData>(
                replacement_data)
                ->lastTouchTick = curTick();
        }

        void
        NMRU::reset(const std::shared_ptr<ReplacementData> &replacement_data) const
        {
            auto repl_data = std::static_pointer_cast<NMRUReplData>(replacement_data);
            // Set last touch timestamp
            repl_data->lastTouchTick = curTick();
            // Mark entry as valid
            repl_data->valid = true;
        }

        ReplaceableEntry *
        NMRU::getVictim(const ReplacementCandidates &candidates) const
        {
            // There must be at least one replacement candidate
            assert(candidates.size() > 0);

            // Visit all candidates to find MRU
            ReplaceableEntry *mru = candidates[0];
            for (const auto &candidate : candidates)
            {
                if (std::static_pointer_cast<NMRUReplData>(
                        candidate->replacementData)
                        ->lastTouchTick >
                    std::static_pointer_cast<NMRUReplData>(
                        mru->replacementData)
                        ->lastTouchTick)
                {
                    mru = candidate;
                }
            }

            // Create a list of candidates excluding the MRU
            std::vector<ReplaceableEntry *> non_mru_candidates;

            for (const auto &candidate : candidates)
            {
                if (candidate != mru)
                {
                    non_mru_candidates.push_back(candidate);
                }
            }

            // If all entries except the MRU are invalid, we must evict the MRU
            if (non_mru_candidates.empty())
            {
                return mru;
            }

            // Select a random entry from the non-MRU candidates

            ReplaceableEntry *victim = non_mru_candidates[rng->random<unsigned>(0, non_mru_candidates.size() - 1)];

            // Visit all candidates to search for an invalid entry. If one is found,
            // its eviction is prioritized
            for (const auto &candidate : candidates)
            {
                if (!std::static_pointer_cast<NMRUReplData>(
                         candidate->replacementData)
                         ->valid)
                {
                    victim = candidate;
                    break;
                }
            }
            return victim;
        }

        std::shared_ptr<ReplacementData>
        NMRU::instantiateEntry()
        {
            return std::shared_ptr<ReplacementData>(new NMRUReplData());
        }

    } // namespace replacement_policy
} // namespace gem5
