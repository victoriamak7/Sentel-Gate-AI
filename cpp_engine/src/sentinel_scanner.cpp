#include "sentinel_scanner.hpp"
#include <cmath>
#include <array>
#include <algorithm>

namespace sentinel {

SentinelScanner::SentinelScanner() {
    // 1. Confidential & Credential patterns (CONFIDENTIAL_BLOCKED)
    confidential_patterns_ = {
        {"AWS_ACCESS_KEY", std::regex(R"((?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16})")},
        {"DB_CONNECTION_STRING", std::regex(R"((postgres|mysql|mongodb|redis|amqp|mssql):\/\/[a-zA-Z0-9_.-]+:[^@\s]+@[a-zA-Z0-9_.-]+(?::[0-9]+)?\/[a-zA-Z0-9_.-]*)")},
        {"PRIVATE_KEY_HEADER", std::regex(R"(-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----)")},
        {"GENERIC_API_KEY", std::regex(R"((?:api[_-]?key|secret[_-]?key|access[_-]?token|bearer[_-]?token)\s*[:=]\s*['"]?[a-zA-Z0-9_\-\.]{16,}['"]?)", std::regex_constants::icase)},
        {"GITHUB_TOKEN", std::regex(R"(gh[pousr]_[A-Za-z0-9_]{36,255})")},
        {"OPENAI_SECRET_KEY", std::regex(R"(sk-[a-zA-Z0-9]{20,48})")},
        {"INTERNAL_ENV_LEAK", std::regex(R"((?:SECRET|PASSWORD|PASSWD|DATABASE_URL|MASTER_KEY|AUTH_SECRET)\s*=\s*[^\s]+)", std::regex_constants::icase)}
    };

    // 2. Sensitive PII patterns (SENSITIVE_PII)
    pii_patterns_ = {
        {"EMAIL_ADDRESS", std::regex(R"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})")},
        {"PHONE_NUMBER", std::regex(R"((?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})")},
        {"US_SSN", std::regex(R"(\b\d{3}-\d{2}-\d{4}\b)")},
        {"CREDIT_CARD", std::regex(R"(\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b)")}
    };
}

double SentinelScanner::calculate_entropy(std::string_view text) {
    if (text.empty()) return 0.0;
    std::array<size_t, 256> frequencies = {0};
    for (char c : text) {
        frequencies[static_cast<unsigned char>(c)]++;
    }

    double entropy = 0.0;
    double len = static_cast<double>(text.length());
    for (size_t count : frequencies) {
        if (count > 0) {
            double p = static_cast<double>(count) / len;
            entropy -= p * std::log2(p);
        }
    }
    return entropy;
}

ScanResult SentinelScanner::inspect(std::string_view input) {
    auto start_time = std::chrono::high_resolution_clock::now();

    ScanResult result;
    result.category = ClassificationCategory::PUBLIC_SAFE;
    result.confidence = 0.99;
    result.matched_rule = "NONE";
    result.snippet_preview = "";
    result.requires_blocking = false;
    result.requires_redaction = false;

    std::string text(input);

    // First check: confidential patterns (immediate hard block)
    for (const auto& [rule_name, pattern] : confidential_patterns_) {
        std::smatch match;
        if (std::regex_search(text, match, pattern)) {
            result.category = ClassificationCategory::CONFIDENTIAL_BLOCKED;
            result.confidence = 0.98;
            result.matched_rule = rule_name;
            result.snippet_preview = match.str().substr(0, 32) + "...";
            result.requires_blocking = true;
            result.requires_redaction = false;
            
            auto end_time = std::chrono::high_resolution_clock::now();
            result.scan_latency_ms = std::chrono::duration<double, std::milli>(end_time - start_time).count();
            return result;
        }
    }

    // Second check: PII patterns (redaction required)
    for (const auto& [rule_name, pattern] : pii_patterns_) {
        std::smatch match;
        if (std::regex_search(text, match, pattern)) {
            result.category = ClassificationCategory::SENSITIVE_PII;
            result.confidence = 0.95;
            result.matched_rule = rule_name;
            result.snippet_preview = match.str();
            result.requires_blocking = false;
            result.requires_redaction = true;
            
            auto end_time = std::chrono::high_resolution_clock::now();
            result.scan_latency_ms = std::chrono::duration<double, std::milli>(end_time - start_time).count();
            return result;
        }
    }

    // Check entropy for random high-entropy hex/base64 secrets
    if (text.length() >= 24 && calculate_entropy(text) > 4.5 && text.find(' ') == std::string::npos) {
        result.category = ClassificationCategory::UNCERTAIN_REVIEW;
        result.confidence = 0.75;
        result.matched_rule = "HIGH_ENTROPY_TOKEN";
        result.snippet_preview = text.substr(0, 16) + "...";
        result.requires_blocking = false;
        result.requires_redaction = false;
    }

    auto end_time = std::chrono::high_resolution_clock::now();
    result.scan_latency_ms = std::chrono::duration<double, std::milli>(end_time - start_time).count();
    return result;
}

} // namespace sentinel
