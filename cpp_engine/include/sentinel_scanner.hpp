#pragma once

#include <string>
#include <string_view>
#include <vector>
#include <regex>
#include <chrono>

namespace sentinel {

enum class ClassificationCategory {
    PUBLIC_SAFE = 0,
    SENSITIVE_PII = 1,
    CONFIDENTIAL_BLOCKED = 2,
    UNCERTAIN_REVIEW = 3
};

struct ScanResult {
    ClassificationCategory category;
    double confidence;
    double scan_latency_ms;
    std::string matched_rule;
    std::string snippet_preview;
    bool requires_blocking;
    bool requires_redaction;
};

class SentinelScanner {
public:
    SentinelScanner();
    ~SentinelScanner() = default;

    // High-speed zero-copy string inspection in C++20
    ScanResult inspect(std::string_view input);

    // Fast Shannon entropy calculator for secret detection
    static double calculate_entropy(std::string_view text);

private:
    std::vector<std::pair<std::string, std::regex>> confidential_patterns_;
    std::vector<std::pair<std::string, std::regex>> pii_patterns_;
};

} // namespace sentinel
