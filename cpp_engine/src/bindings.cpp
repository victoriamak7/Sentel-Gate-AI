#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "sentinel_scanner.hpp"

namespace py = pybind11;
using namespace sentinel;

PYBIND11_MODULE(sentinel_cpp_scanner, m) {
    m.doc() = "C++20 Zero-Copy Pattern Inspection Engine for Sentinel-Gate AI";

    py::enum_<ClassificationCategory>(m, "ClassificationCategory")
        .value("PUBLIC_SAFE", ClassificationCategory::PUBLIC_SAFE)
        .value("SENSITIVE_PII", ClassificationCategory::SENSITIVE_PII)
        .value("CONFIDENTIAL_BLOCKED", ClassificationCategory::CONFIDENTIAL_BLOCKED)
        .value("UNCERTAIN_REVIEW", ClassificationCategory::UNCERTAIN_REVIEW)
        .export_values();

    py::class_<ScanResult>(m, "ScanResult")
        .def_readonly("category", &ScanResult::category)
        .def_readonly("confidence", &ScanResult::confidence)
        .def_readonly("scan_latency_ms", &ScanResult::scan_latency_ms)
        .def_readonly("matched_rule", &ScanResult::matched_rule)
        .def_readonly("snippet_preview", &ScanResult::snippet_preview)
        .def_readonly("requires_blocking", &ScanResult::requires_blocking)
        .def_readonly("requires_redaction", &ScanResult::requires_redaction);

    py::class_<SentinelScanner>(m, "SentinelScanner")
        .def(py::init<>())
        .def("inspect", &SentinelScanner::inspect, "Inspect input text using zero-copy C++20 engine")
        .def_static("calculate_entropy", &SentinelScanner::calculate_entropy, "Calculate Shannon entropy of text");
}
