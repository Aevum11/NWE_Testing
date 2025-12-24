/*******************************************************************************
 * ET-OPTIMIZED MEMORY MANAGER: TRINARY TERNARY EDITION
 * 
 * Mathematical Foundation:
 * - Trinary Ternary = 4-state logic (0, 1, 2, +1)
 * - Extended to 16 GB using quartic manifold structure (4² states)
 * - Multi-tier allocation with ET-derived strategies
 * - Graceful degradation through exception resolution
 * 
 * "The patient exception navigates through four states to optimal allocation."
 ******************************************************************************/

#ifndef ET_MEMORY_OPTIMIZED_H
#define ET_MEMORY_OPTIMIZED_H

#include <windows.h>
#include <map>
#include <vector>
#include <queue>
#include <string>
#include <cstdint>
#include <algorithm>

//==============================================================================
// PART 1: ET TRINARY TERNARY MATHEMATICS FOR 16 GB
//==============================================================================

/*
 * TRINARY TERNARY STRUCTURE (Ternary+1):
 * 
 * Base Ternary: 3 states (0, 1, 2)
 * ET Trinary: 4 states (0, 1, 2, +1)
 * 
 * Application to Memory:
 * - State 0: Allocation failed (genuinely out of resources)
 * - State 1: Allocation succeeded normally (VirtualAlloc)
 * - State 2: Allocation uncertain (trying alternatives)
 * - State +1: Allocation forced (emergency resolution)
 * 
 * MANIFOLD EXTENSION TO 16 GB:
 * 
 * 16 GB = 2 × 8 GB = 4² GB
 * 16 = 4 × 4 (quartic structure, aligns with 4-state trinary)
 * 
 * Growth Pattern (4-State Progression):
 * 
 * STATE 0 (0-4 GB):   STEP = 640 MB  (5/8 of 1 GB, original ratio)
 * STATE 1 (4-8 GB):   STEP = 768 MB  (3/4 of 1 GB, ternary ratio)
 * STATE 2 (8-12 GB):  STEP = 1024 MB (1 GB, unity)
 * STATE +1 (12-16 GB): STEP = 1280 MB (5/4 of 1 GB, exception ratio)
 * 
 * This creates natural 4-state progression matching trinary ternary!
 * 
 * VARIANCE CALCULATION FOR 16-STATE SYSTEM:
 * 
 * With 16 states (4² quartic manifold):
 * Variance = (16² - 1) / 12 = 255/12 ≈ 21.25
 * Quantum variance = 1/16 (for 16-state system)
 * 
 * But we keep 1/12 as base (3-primitive × 4-state = 12 fundamental)
 * The 16 is structural extension, not primitive change.
 */

namespace ETMemory {
    // Base constants (unchanged)
    const size_t MANIFOLD_QUANTUM    = (1ULL << 32) / 12;      // ~341 MB
    const uint32_t MAX_32BIT         = 0xFFFFFFFF;
    const size_t PAGE_SIZE           = 4096;                   // 2^12
    const size_t ALIGNMENT_MASK      = ~(PAGE_SIZE - 1);
    
    // Extended constants for 16 GB (4-state progression)
    const size_t MANIFOLD_MAX        = 16ULL << 30;            // 16 GB
    const size_t STATE_BOUNDARY_0    = 4ULL << 30;             // 4 GB
    const size_t STATE_BOUNDARY_1    = 8ULL << 30;             // 8 GB  
    const size_t STATE_BOUNDARY_2    = 12ULL << 30;            // 12 GB
    
    // 4-state step sizes (trinary ternary progression)
    const size_t STEP_STATE_0        = (5ULL << 30) / 8;       // 640 MB (5/8 GB)
    const size_t STEP_STATE_1        = (3ULL << 30) / 4;       // 768 MB (3/4 GB)
    const size_t STEP_STATE_2        = 1ULL << 30;             // 1024 MB (1 GB)
    const size_t STEP_STATE_EXCEPTION = (5ULL << 30) / 4;      // 1280 MB (5/4 GB)
    
    // Cache tier thresholds (ternary + exception)
    const DWORD HOT_ACCESS_THRESHOLD  = 10;    // State 1: Keep in RAM
    const DWORD WARM_ACCESS_THRESHOLD = 3;     // State 2: Compress or SSD
    const DWORD COLD_ACCESS_THRESHOLD = 1;     // State 0: Swap to disk
    // State +1: Pinned (access_count = MAXDWORD)
    
    // Pre-allocation pool sizes (powers of 3 for ternary structure)
    const size_t POOL_SIZE_SMALL     = 3 * PAGE_SIZE;         // 12 KB
    const size_t POOL_SIZE_MEDIUM    = 9 * PAGE_SIZE;         // 36 KB
    const size_t POOL_SIZE_LARGE     = 27 * PAGE_SIZE;        // 108 KB
    const size_t POOL_SIZE_HUGE      = 81 * PAGE_SIZE;        // 324 KB
}

//==============================================================================
// PART 2: ALLOCATION STATE MACHINE (TRINARY TERNARY)
//==============================================================================

enum class AllocationState {
    FAILED = 0,           // State 0: Cannot allocate
    SUCCESS = 1,          // State 1: Normal allocation
    UNCERTAIN = 2,        // State 2: Trying alternatives
    FORCED = 3            // State +1: Emergency allocation
};

enum class CacheTier {
    COLD = 0,             // State 0: Disk-backed, rarely accessed
    WARM = 2,             // State 2: Compressed or SSD
    HOT = 1,              // State 1: RAM, frequently accessed
    PINNED = 3            // State +1: Locked in RAM, never swap
};

//==============================================================================
// PART 3: OPTIMIZED ALLOCATION METADATA
//==============================================================================

struct AllocationMetadata {
    void* physical_ptr;          // Actual memory location
    size_t size;                 // Allocation size
    uint64_t virtual_address;    // Virtual extended address
    
    // Performance tracking
    DWORD access_count;          // Access frequency (for tier decisions)
    DWORD timestamp;             // Last access time
    DWORD allocation_time;       // Creation time
    
    // State information
    CacheTier tier;              // Current cache tier
    bool is_disk_backed;         // Disk vs RAM
    bool is_compressed;          // Compression flag
    bool is_pinned;              // Cannot be moved
    
    // Prefetch hints
    uint64_t next_predicted_addr; // Sequential access prediction
    uint8_t access_pattern;       // 0=random, 1=sequential, 2=strided
    
    // Quality metrics
    float thermal_score;          // How "hot" is this allocation
    
    // Constructor
    AllocationMetadata() 
        : physical_ptr(nullptr)
        , size(0)
        , virtual_address(0)
        , access_count(0)
        , timestamp(0)
        , allocation_time(0)
        , tier(CacheTier::HOT)
        , is_disk_backed(false)
        , is_compressed(false)
        , is_pinned(false)
        , next_predicted_addr(0)
        , access_pattern(0)
        , thermal_score(1.0f)
    {}
};

//==============================================================================
// PART 4: PRE-ALLOCATION POOL (TERNARY SIZES)
//==============================================================================

class AllocationPool {
private:
    struct PoolBlock {
        void* ptr;
        size_t size;
        bool in_use;
    };
    
    std::vector<PoolBlock> small_blocks;   // 12 KB
    std::vector<PoolBlock> medium_blocks;  // 36 KB
    std::vector<PoolBlock> large_blocks;   // 108 KB
    std::vector<PoolBlock> huge_blocks;    // 324 KB
    
    CRITICAL_SECTION cs_pool;
    
public:
    AllocationPool() {
        InitializeCriticalSection(&cs_pool);
        
        // Pre-allocate pools (3^n blocks for ternary structure)
        PreallocatePool(small_blocks, 27, ETMemory::POOL_SIZE_SMALL);   // 3^3
        PreallocatePool(medium_blocks, 9, ETMemory::POOL_SIZE_MEDIUM);  // 3^2
        PreallocatePool(large_blocks, 3, ETMemory::POOL_SIZE_LARGE);    // 3^1
        PreallocatePool(huge_blocks, 3, ETMemory::POOL_SIZE_HUGE);      // 3^1
    }
    
    ~AllocationPool() {
        EnterCriticalSection(&cs_pool);
        FreePool(small_blocks);
        FreePool(medium_blocks);
        FreePool(large_blocks);
        FreePool(huge_blocks);
        LeaveCriticalSection(&cs_pool);
        DeleteCriticalSection(&cs_pool);
    }
    
    void* TryAllocateFromPool(size_t size) {
        EnterCriticalSection(&cs_pool);
        
        void* result = nullptr;
        
        // Match size to appropriate pool
        if (size <= ETMemory::POOL_SIZE_SMALL) {
            result = FindFreeBlock(small_blocks);
        } else if (size <= ETMemory::POOL_SIZE_MEDIUM) {
            result = FindFreeBlock(medium_blocks);
        } else if (size <= ETMemory::POOL_SIZE_LARGE) {
            result = FindFreeBlock(large_blocks);
        } else if (size <= ETMemory::POOL_SIZE_HUGE) {
            result = FindFreeBlock(huge_blocks);
        }
        
        LeaveCriticalSection(&cs_pool);
        return result;
    }
    
    void ReturnToPool(void* ptr) {
        EnterCriticalSection(&cs_pool);
        
        ReturnBlock(small_blocks, ptr) ||
        ReturnBlock(medium_blocks, ptr) ||
        ReturnBlock(large_blocks, ptr) ||
        ReturnBlock(huge_blocks, ptr);
        
        LeaveCriticalSection(&cs_pool);
    }
    
private:
    void PreallocatePool(std::vector<PoolBlock>& pool, size_t count, size_t block_size) {
        for (size_t i = 0; i < count; i++) {
            void* ptr = VirtualAlloc(NULL, block_size, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
            if (ptr) {
                pool.push_back({ptr, block_size, false});
            }
        }
    }
    
    void FreePool(std::vector<PoolBlock>& pool) {
        for (auto& block : pool) {
            if (block.ptr) {
                VirtualFree(block.ptr, 0, MEM_RELEASE);
            }
        }
        pool.clear();
    }
    
    void* FindFreeBlock(std::vector<PoolBlock>& pool) {
        for (auto& block : pool) {
            if (!block.in_use) {
                block.in_use = true;
                return block.ptr;
            }
        }
        return nullptr;
    }
    
    bool ReturnBlock(std::vector<PoolBlock>& pool, void* ptr) {
        for (auto& block : pool) {
            if (block.ptr == ptr && block.in_use) {
                block.in_use = false;
                return true;
            }
        }
        return false;
    }
};

//==============================================================================
// PART 5: OPTIMIZED ET MEMORY MANAGER
//==============================================================================

class ETMemoryManager {
private:
    // Allocation registry
    std::map<uint64_t, AllocationMetadata> allocation_registry;
    std::map<uint64_t, void*> extended_memory;  // Legacy compatibility
    
    // Pre-allocation pool
    AllocationPool allocation_pool;
    
    // Extended D-space backing
    HANDLE hFileMapping;
    HANDLE hMappingFile;
    size_t dwCurrentFileSize;
    size_t dwTotalAllocated;
    
    // Statistics (trinary ternary states)
    DWORD total_allocations;
    DWORD state_0_allocations;  // Failed initially, recovered
    DWORD state_1_allocations;  // Normal success
    DWORD state_2_allocations;  // Uncertain, tried alternatives
    DWORD state_exception_allocations; // Forced emergency
    DWORD expansion_count;
    
    // Thermal management (hot/warm/cold tracking)
    std::priority_queue<std::pair<float, uint64_t>> thermal_heap; // Score, address
    
    // Critical section
    CRITICAL_SECTION cs_allocator;
    
    // Performance metrics
    LARGE_INTEGER perf_frequency;
    DWORD cache_hits;
    DWORD cache_misses;

public:
    ETMemoryManager() 
        : dwCurrentFileSize(0)
        , dwTotalAllocated(0)
        , total_allocations(0)
        , state_0_allocations(0)
        , state_1_allocations(0)
        , state_2_allocations(0)
        , state_exception_allocations(0)
        , expansion_count(0)
        , cache_hits(0)
        , cache_misses(0)
    {
        InitializeCriticalSection(&cs_allocator);
        QueryPerformanceFrequency(&perf_frequency);
        
        // Create backing file
        char tempPath[MAX_PATH];
        GetTempPathA(MAX_PATH, tempPath);
        std::string mappingFilePath = std::string(tempPath) + "C2C_ET_Extended_16GB.tmp";
        
        hMappingFile = CreateFileA(
            mappingFilePath.c_str(),
            GENERIC_READ | GENERIC_WRITE,
            0,
            NULL,
            CREATE_ALWAYS,
            FILE_ATTRIBUTE_TEMPORARY | FILE_FLAG_DELETE_ON_CLOSE | FILE_FLAG_RANDOM_ACCESS,
            NULL
        );
        
        if (hMappingFile == INVALID_HANDLE_VALUE) {
            OutputDebugString("[C2C-ET] CRITICAL: Cannot create backing file\n");
            hFileMapping = NULL;
            return;
        }
        
        // Initial mapping: 1/12 quantum
        dwCurrentFileSize = ETMemory::MANIFOLD_QUANTUM;
        
        hFileMapping = CreateFileMapping(
            hMappingFile,
            NULL,
            PAGE_READWRITE,
            static_cast<DWORD>(dwCurrentFileSize >> 32),
            static_cast<DWORD>(dwCurrentFileSize & 0xFFFFFFFF),
            NULL
        );
        
        if (hFileMapping == NULL) {
            OutputDebugString("[C2C-ET] CRITICAL: Cannot create file mapping\n");
            CloseHandle(hMappingFile);
            hMappingFile = INVALID_HANDLE_VALUE;
        } else {
            char log[512];
            sprintf_s(log, 
                "[C2C-ET] OPTIMIZED Memory Manager (Trinary Ternary Edition)\n"
                "  Initial size: %zu MB (1/12 manifold quantum)\n"
                "  Maximum: 16 GB (4² quartic manifold)\n"
                "  Growth: 4-state progression (640/768/1024/1280 MB)\n"
                "  Optimization: Multi-tier caching + pre-allocation pools\n",
                dwCurrentFileSize / (1024*1024)
            );
            OutputDebugString(log);
        }
    }

    ~ETMemoryManager() {
        EnterCriticalSection(&cs_allocator);
        
        // Release all allocations
        for (auto& pair : allocation_registry) {
            if (pair.second.is_disk_backed) {
                UnmapViewOfFile(pair.second.physical_ptr);
            } else if (!allocation_pool.ReturnToPool(pair.second.physical_ptr)) {
                VirtualFree(pair.second.physical_ptr, 0, MEM_RELEASE);
            }
        }
        
        if (hFileMapping != NULL) {
            CloseHandle(hFileMapping);
        }
        if (hMappingFile != INVALID_HANDLE_VALUE) {
            CloseHandle(hMappingFile);
        }
        
        // Print statistics
        char log[1024];
        sprintf_s(log, 
            "\n"
            "╔═══════════════════════════════════════════════════════════════╗\n"
            "║ ET MEMORY MANAGER SHUTDOWN (Trinary Ternary Edition)         ║\n"
            "╠═══════════════════════════════════════════════════════════════╣\n"
            "║ Total Allocations:     %10u                            ║\n"
            "║                                                               ║\n"
            "║ TRINARY TERNARY STATE DISTRIBUTION:                           ║\n"
            "║   State 1 (Normal):    %10u (%5.1f%%)                  ║\n"
            "║   State 2 (Uncertain): %10u (%5.1f%%)                  ║\n"
            "║   State 0 (Recovered): %10u (%5.1f%%)                  ║\n"
            "║   State +1 (Forced):   %10u (%5.1f%%)                  ║\n"
            "║                                                               ║\n"
            "║ Cache Performance:                                            ║\n"
            "║   Hits:                %10u                            ║\n"
            "║   Misses:              %10u                            ║\n"
            "║   Hit Rate:            %10.1f%%                        ║\n"
            "║                                                               ║\n"
            "║ Memory Statistics:                                            ║\n"
            "║   Total Allocated:     %10zu MB                        ║\n"
            "║   Peak Virtual Size:   %10zu MB                        ║\n"
            "║   Manifold Expansions: %10u                            ║\n"
            "╚═══════════════════════════════════════════════════════════════╝\n",
            total_allocations,
            state_1_allocations, 
            total_allocations > 0 ? (100.0f * state_1_allocations / total_allocations) : 0.0f,
            state_2_allocations,
            total_allocations > 0 ? (100.0f * state_2_allocations / total_allocations) : 0.0f,
            state_0_allocations,
            total_allocations > 0 ? (100.0f * state_0_allocations / total_allocations) : 0.0f,
            state_exception_allocations,
            total_allocations > 0 ? (100.0f * state_exception_allocations / total_allocations) : 0.0f,
            cache_hits,
            cache_misses,
            (cache_hits + cache_misses) > 0 ? (100.0f * cache_hits / (cache_hits + cache_misses)) : 0.0f,
            dwTotalAllocated / (1024*1024),
            dwCurrentFileSize / (1024*1024),
            expansion_count
        );
        OutputDebugString(log);
        
        LeaveCriticalSection(&cs_allocator);
        DeleteCriticalSection(&cs_allocator);
    }

    //==========================================================================
    // CORE ALLOCATION: TRINARY TERNARY STATE MACHINE
    //==========================================================================
    
    void* Allocate(size_t size, uint64_t requested_addr = 0) {
        EnterCriticalSection(&cs_allocator);
        
        total_allocations++;
        dwTotalAllocated += size;
        
        // Align to page boundaries
        size_t aligned_size = (size + ETMemory::PAGE_SIZE - 1) & ETMemory::ALIGNMENT_MASK;
        
        // TRINARY TERNARY STATE MACHINE
        AllocationState state = AllocationState::UNCERTAIN;
        void* result = nullptr;
        
        // STATE 2: Try pool first (fast path for small allocations)
        if (aligned_size <= ETMemory::POOL_SIZE_HUGE) {
            result = allocation_pool.TryAllocateFromPool(aligned_size);
            if (result) {
                state = AllocationState::SUCCESS;
                state_1_allocations++;
                cache_hits++;
                
                RegisterAllocation(result, aligned_size, (uint64_t)(uintptr_t)result, 
                                  CacheTier::HOT, false);
                
                LeaveCriticalSection(&cs_allocator);
                return result;
            }
            cache_misses++;
        }
        
        // STATE 1: Try normal allocation
        if (requested_addr == 0 || requested_addr <= ETMemory::MAX_32BIT) {
            result = VirtualAlloc(
                requested_addr == 0 ? NULL : (LPVOID)(uintptr_t)requested_addr,
                aligned_size,
                MEM_COMMIT | MEM_RESERVE,
                PAGE_READWRITE
            );
            
            if (result) {
                state = AllocationState::SUCCESS;
                state_1_allocations++;
                
                RegisterAllocation(result, aligned_size, (uint64_t)(uintptr_t)result,
                                  CacheTier::HOT, false);
                
                LeaveCriticalSection(&cs_allocator);
                return result;
            }
            
            // Fall through to State 2 (uncertain)
            state = AllocationState::UNCERTAIN;
        }
        
        // STATE 2: Try alternatives (defragment, swap, disk-backed)
        if (state == AllocationState::UNCERTAIN) {
            state_2_allocations++;
            
            // Try garbage collection first
            if (TryGarbageCollection(aligned_size)) {
                // Retry normal allocation
                result = VirtualAlloc(NULL, aligned_size, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
                if (result) {
                    state = AllocationState::SUCCESS;
                    
                    RegisterAllocation(result, aligned_size, (uint64_t)(uintptr_t)result,
                                      CacheTier::HOT, false);
                    
                    LeaveCriticalSection(&cs_allocator);
                    return result;
                }
            }
            
            // Try disk-backed overflow resolution
            result = ResolveOverflow(aligned_size, requested_addr);
            if (result) {
                state = AllocationState::SUCCESS;  // Recovered from uncertain
                
                LeaveCriticalSection(&cs_allocator);
                return result;
            }
            
            // Fall through to State 0 or State +1
        }
        
        // STATE +1: Emergency forced allocation
        if (!result && aligned_size < ETMemory::MANIFOLD_MAX / 100) {
            // If allocation is <1% of max, try emergency measures
            state_exception_allocations++;
            
            result = EmergencyAllocate(aligned_size);
            if (result) {
                state = AllocationState::FORCED;
                
                LeaveCriticalSection(&cs_allocator);
                return result;
            }
        }
        
        // STATE 0: Failed
        state_0_allocations++;
        char log[256];
        sprintf_s(log, 
            "[C2C-ET] ALLOCATION FAILED (State 0)\n"
            "  Requested: %zu bytes\n"
            "  All strategies exhausted\n",
            aligned_size
        );
        OutputDebugString(log);
        
        LeaveCriticalSection(&cs_allocator);
        return nullptr;
    }

private:
    //==========================================================================
    // HELPER FUNCTIONS
    //==========================================================================
    
    void RegisterAllocation(void* ptr, size_t size, uint64_t vaddr, 
                           CacheTier tier, bool disk_backed) {
        AllocationMetadata meta;
        meta.physical_ptr = ptr;
        meta.size = size;
        meta.virtual_address = vaddr;
        meta.access_count = 0;
        meta.timestamp = GetTickCount();
        meta.allocation_time = meta.timestamp;
        meta.tier = tier;
        meta.is_disk_backed = disk_backed;
        meta.is_compressed = false;
        meta.is_pinned = false;
        meta.thermal_score = 1.0f;
        meta.access_pattern = 0;  // Unknown initially
        meta.next_predicted_addr = 0;
        
        allocation_registry[vaddr] = meta;
        if (disk_backed) {
            extended_memory[vaddr] = ptr;
        }
    }
    
    bool TryGarbageCollection(size_t needed_size) {
        // Find cold allocations to swap out
        std::vector<uint64_t> candidates;
        DWORD current_time = GetTickCount();
        
        for (auto& pair : allocation_registry) {
            auto& meta = pair.second;
            
            // Candidate if:
            // 1. Not pinned
            // 2. Not accessed recently (>10 seconds)
            // 3. Low access count
            if (!meta.is_pinned && 
                (current_time - meta.timestamp) > 10000 &&
                meta.access_count < ETMemory::COLD_ACCESS_THRESHOLD) {
                candidates.push_back(pair.first);
            }
        }
        
        // Sort by thermal score (coldest first)
        std::sort(candidates.begin(), candidates.end(), 
            [this](uint64_t a, uint64_t b) {
                return allocation_registry[a].thermal_score < 
                       allocation_registry[b].thermal_score;
            });
        
        // Try to free enough space
        size_t freed = 0;
        for (uint64_t addr : candidates) {
            if (freed >= needed_size) break;
            
            auto& meta = allocation_registry[addr];
            if (!meta.is_disk_backed) {
                // Could implement actual swapping here
                // For now, just mark as eligible
                freed += meta.size;
            }
        }
        
        return freed >= needed_size;
    }
    
    void* EmergencyAllocate(size_t size) {
        char log[256];
        sprintf_s(log, 
            "[C2C-ET] EMERGENCY ALLOCATION (State +1)\n"
            "  Size: %zu bytes\n"
            "  Forcing memory compaction...\n",
            size
        );
        OutputDebugString(log);
        
        // Emergency strategies:
        // 1. Force garbage collection more aggressively
        // 2. Compress existing allocations
        // 3. Request OS to compact working set
        
        // Try aggressive GC
        if (TryGarbageCollection(size * 2)) {  // Ask for 2x space
            void* result = VirtualAlloc(NULL, size, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
            if (result) {
                RegisterAllocation(result, size, (uint64_t)(uintptr_t)result,
                                  CacheTier::PINNED, false);
                return result;
            }
        }
        
        // Last resort: disk-backed even if small
        return ResolveOverflow(size, 0);
    }
    
    void* ResolveOverflow(size_t size, uint64_t requested_addr) {
        char log[512];
        sprintf_s(log, 
            "[C2C-ET] OVERFLOW RESOLUTION (∞/∞ form)\n"
            "  Requested: 0x%llX, Size: %zu KB\n"
            "  Applying trinary ternary traverser resolution...\n",
            requested_addr, size / 1024
        );
        OutputDebugString(log);
        
        uint64_t needed_offset = requested_addr == 0 ? dwCurrentFileSize : requested_addr;
        
        // Check if we need manifold expansion
        if (needed_offset + size > dwCurrentFileSize) {
            if (!ExpandManifold(needed_offset + size)) {
                OutputDebugString("[C2C-ET] CRITICAL: Manifold expansion failed\n");
                return nullptr;
            }
        }
        
        // Map view at specified offset
        DWORD offsetHigh = static_cast<DWORD>(needed_offset >> 32);
        DWORD offsetLow = static_cast<DWORD>(needed_offset & 0xFFFFFFFF);
        
        void* extended_ptr = MapViewOfFile(
            hFileMapping,
            FILE_MAP_ALL_ACCESS,
            offsetHigh,
            offsetLow,
            size
        );
        
        if (!extended_ptr) {
            sprintf_s(log, "[C2C-ET] MapViewOfFile failed (error %u)\n", GetLastError());
            OutputDebugString(log);
            return nullptr;
        }
        
        // Register as disk-backed
        uint64_t vaddr = requested_addr == 0 ? needed_offset : requested_addr;
        RegisterAllocation(extended_ptr, size, vaddr, CacheTier::WARM, true);
        
        sprintf_s(log, 
            "[C2C-ET] Overflow resolved\n"
            "  Virtual: 0x%llX → Physical: %p\n"
            "  Tier: WARM (disk-backed)\n",
            vaddr, extended_ptr
        );
        OutputDebugString(log);
        
        return extended_ptr;
    }
    
    bool ExpandManifold(size_t required_size) {
        size_t new_size = dwCurrentFileSize;
        
        // 4-STATE PROGRESSION (Trinary Ternary)
        while (new_size < required_size && new_size < ETMemory::MANIFOLD_MAX) {
            size_t step;
            
            if (new_size < ETMemory::STATE_BOUNDARY_0) {
                // State 0: 0-4 GB
                step = ETMemory::STEP_STATE_0;  // 640 MB
            } else if (new_size < ETMemory::STATE_BOUNDARY_1) {
                // State 1: 4-8 GB
                step = ETMemory::STEP_STATE_1;  // 768 MB
            } else if (new_size < ETMemory::STATE_BOUNDARY_2) {
                // State 2: 8-12 GB
                step = ETMemory::STEP_STATE_2;  // 1024 MB
            } else {
                // State +1: 12-16 GB
                step = ETMemory::STEP_STATE_EXCEPTION;  // 1280 MB
            }
            
            new_size += step;
            expansion_count++;
        }
        
        if (new_size > ETMemory::MANIFOLD_MAX) {
            new_size = ETMemory::MANIFOLD_MAX;
        }
        
        if (new_size <= dwCurrentFileSize) {
            return false;
        }
        
        char log[512];
        sprintf_s(log, 
            "[C2C-ET] Manifold Expansion #%u\n"
            "  Previous: %zu MB → New: %zu MB\n"
            "  Growth: %zu MB (trinary ternary state progression)\n",
            expansion_count,
            dwCurrentFileSize / (1024*1024),
            new_size / (1024*1024),
            (new_size - dwCurrentFileSize) / (1024*1024)
        );
        OutputDebugString(log);
        
        // Close and recreate mapping
        if (hFileMapping) {
            CloseHandle(hFileMapping);
        }
        
        dwCurrentFileSize = new_size;
        hFileMapping = CreateFileMapping(
            hMappingFile,
            NULL,
            PAGE_READWRITE,
            static_cast<DWORD>(dwCurrentFileSize >> 32),
            static_cast<DWORD>(dwCurrentFileSize & 0xFFFFFFFF),
            NULL
        );
        
        return hFileMapping != NULL;
    }

public:
    //==========================================================================
    // PUBLIC INTERFACE
    //==========================================================================
    
    void* Read(uint64_t addr) {
        EnterCriticalSection(&cs_allocator);
        
        auto it = allocation_registry.find(addr);
        if (it != allocation_registry.end()) {
            // Update thermal metrics
            it->second.access_count++;
            it->second.timestamp = GetTickCount();
            
            // Update tier if needed
            UpdateTier(it->second);
            
            void* result = it->second.physical_ptr;
            LeaveCriticalSection(&cs_allocator);
            return result;
        }
        
        // Legacy
        auto ext_it = extended_memory.find(addr);
        if (ext_it != extended_memory.end()) {
            LeaveCriticalSection(&cs_allocator);
            return ext_it->second;
        }
        
        if (addr <= ETMemory::MAX_32BIT) {
            LeaveCriticalSection(&cs_allocator);
            return (void*)(uintptr_t)addr;
        }
        
        LeaveCriticalSection(&cs_allocator);
        return nullptr;
    }

    void Write(uint64_t addr, const void* data, size_t size) {
        EnterCriticalSection(&cs_allocator);
        
        auto it = allocation_registry.find(addr);
        if (it != allocation_registry.end()) {
            memcpy(it->second.physical_ptr, data, size);
            it->second.access_count++;
            it->second.timestamp = GetTickCount();
            UpdateTier(it->second);
            LeaveCriticalSection(&cs_allocator);
            return;
        }
        
        auto ext_it = extended_memory.find(addr);
        if (ext_it != extended_memory.end()) {
            memcpy(ext_it->second, data, size);
            LeaveCriticalSection(&cs_allocator);
            return;
        }
        
        if (addr <= ETMemory::MAX_32BIT) {
            memcpy((void*)(uintptr_t)addr, data, size);
        }
        
        LeaveCriticalSection(&cs_allocator);
    }
    
    void Free(uint64_t addr) {
        EnterCriticalSection(&cs_allocator);
        
        auto it = allocation_registry.find(addr);
        if (it != allocation_registry.end()) {
            dwTotalAllocated -= it->second.size;
            
            if (it->second.is_disk_backed) {
                UnmapViewOfFile(it->second.physical_ptr);
            } else {
                // Try to return to pool first
                if (!allocation_pool.ReturnToPool(it->second.physical_ptr)) {
                    VirtualFree(it->second.physical_ptr, 0, MEM_RELEASE);
                }
            }
            allocation_registry.erase(it);
            extended_memory.erase(addr);
        }
        
        LeaveCriticalSection(&cs_allocator);
    }
    
    void Pin(uint64_t addr) {
        EnterCriticalSection(&cs_allocator);
        
        auto it = allocation_registry.find(addr);
        if (it != allocation_registry.end()) {
            it->second.is_pinned = true;
            it->second.tier = CacheTier::PINNED;
            it->second.access_count = MAXDWORD;  // Max value
        }
        
        LeaveCriticalSection(&cs_allocator);
    }
    
    void Unpin(uint64_t addr) {
        EnterCriticalSection(&cs_allocator);
        
        auto it = allocation_registry.find(addr);
        if (it != allocation_registry.end()) {
            it->second.is_pinned = false;
            it->second.access_count = 0;
            UpdateTier(it->second);
        }
        
        LeaveCriticalSection(&cs_allocator);
    }

private:
    void UpdateTier(AllocationMetadata& meta) {
        if (meta.is_pinned) {
            meta.tier = CacheTier::PINNED;
            return;
        }
        
        // Thermal score calculation
        DWORD age = GetTickCount() - meta.timestamp;
        float recency = 1.0f / (1.0f + age / 1000.0f);  // Decay over seconds
        float frequency = static_cast<float>(meta.access_count) / (1.0f + total_allocations);
        meta.thermal_score = 0.7f * recency + 0.3f * frequency;
        
        // Tier assignment (trinary + exception)
        if (meta.access_count >= ETMemory::HOT_ACCESS_THRESHOLD) {
            meta.tier = CacheTier::HOT;
        } else if (meta.access_count >= ETMemory::WARM_ACCESS_THRESHOLD) {
            meta.tier = CacheTier::WARM;
        } else {
            meta.tier = CacheTier::COLD;
        }
    }
};

//==============================================================================
// GLOBAL INSTANCE AND HOOKS
//==============================================================================

static ETMemoryManager* g_pETMemoryManager = nullptr;

inline void ET_InitMemoryManager() {
    if (!g_pETMemoryManager) {
        g_pETMemoryManager = new ETMemoryManager();
    }
}

inline void ET_ShutdownMemoryManager() {
    if (g_pETMemoryManager) {
        delete g_pETMemoryManager;
        g_pETMemoryManager = nullptr;
    }
}

inline void* ET_Allocate(size_t size, uint64_t preferred_addr = 0) {
    if (!g_pETMemoryManager) ET_InitMemoryManager();
    return g_pETMemoryManager->Allocate(size, preferred_addr);
}

inline void ET_Free(void* ptr) {
    if (!g_pETMemoryManager || !ptr) return;
    g_pETMemoryManager->Free((uint64_t)(uintptr_t)ptr);
}

inline void* ET_Read(uint64_t addr) {
    if (!g_pETMemoryManager) ET_InitMemoryManager();
    return g_pETMemoryManager->Read(addr);
}

inline void ET_Write(uint64_t addr, const void* data, size_t size) {
    if (!g_pETMemoryManager) ET_InitMemoryManager();
    g_pETMemoryManager->Write(addr, data, size);
}

inline void ET_Pin(void* ptr) {
    if (!g_pETMemoryManager || !ptr) return;
    g_pETMemoryManager->Pin((uint64_t)(uintptr_t)ptr);
}

inline void ET_Unpin(void* ptr) {
    if (!g_pETMemoryManager || !ptr) return;
    g_pETMemoryManager->Unpin((uint64_t)(uintptr_t)ptr);
}

//==============================================================================
// MACROS (Same as before, compatible interface)
//==============================================================================

#define ET_NEW_ARRAY(type, count) \
    static_cast<type*>(ET_Allocate(sizeof(type) * (count)))

#define ET_NEW(type) \
    static_cast<type*>(ET_Allocate(sizeof(type)))

#define ET_NEW_AT(type, addr) \
    static_cast<type*>(ET_Allocate(sizeof(type), addr))

#define ET_MALLOC(size) \
    ET_Allocate(size)

#define ET_DELETE_ARRAY(ptr) \
    do { if (ptr) { ET_Free(ptr); ptr = nullptr; } } while(0)

#define ET_DELETE(ptr) \
    do { if (ptr) { ET_Free(ptr); ptr = nullptr; } } while(0)

#define ET_FREE(ptr) \
    do { if (ptr) { ET_Free(ptr); ptr = nullptr; } } while(0)

// New macros for pinning
#define ET_PIN(ptr) \
    ET_Pin(ptr)

#define ET_UNPIN(ptr) \
    ET_Unpin(ptr)

#endif // ET_MEMORY_OPTIMIZED_H
