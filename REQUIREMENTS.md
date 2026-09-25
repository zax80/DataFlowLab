# DataFlowLab — Project Requirements

## 1. Project Overview

DataFlowLab is a hands-on Data Engineering project focused on building a reliable, maintainable, and production-oriented ETL pipeline.

The project will progressively evolve from a simple local JSON-based pipeline into a more complete data platform using Python, PostgreSQL, Docker, workflow orchestration, and cloud technologies.

The primary goal is to demonstrate practical Data Engineering skills through a working end-to-end project.

---

## 2. Functional Requirements

### FR-01 — Data Input

The system shall read sales data from a JSON file.

Each record should contain:

* `id`
* `product`
* `price`
* `quantity`

### FR-02 — Data Validation

Each input record shall be validated before processing.

The following rules apply:

* `id` is required.
* `product` is required.
* `price` must be greater than `0`.
* `quantity` must be greater than `0`.

### FR-03 — Invalid Records

Invalid records shall not terminate the entire pipeline.

Invalid records must be logged and excluded from further processing.

### FR-04 — Data Transformation

For each valid record, the pipeline shall calculate:

```text
total = price * quantity
```

The transformed record shall contain the calculated `total` value.

### FR-05 — Data Output

The pipeline shall write successfully processed records to an output JSON file.

### FR-06 — Database Loading

A future version of the pipeline shall load transformed records into a PostgreSQL database.

### FR-07 — Logging

The pipeline shall provide logging for:

* Pipeline start
* Number of input records
* Number of valid records
* Number of invalid records
* Processing errors
* Pipeline completion

---

## 3. Non-Functional Requirements

### NFR-01 — Code Quality

The application shall separate the main ETL responsibilities into distinct components or functions:

```text
Extract
Validate
Transform
Load
```

### NFR-02 — Testability

Core business logic shall be designed so that it can be unit tested independently.

### NFR-03 — Configuration

Application configuration shall not be hardcoded into the source code.

Future versions shall use environment variables or configuration files where appropriate.

### NFR-04 — Reproducibility

A developer should be able to clone the repository and run the project by following the instructions provided in `README.md`.

### NFR-05 — Error Handling

The pipeline shall handle invalid input records and expected processing errors without unnecessarily terminating the entire pipeline.

### NFR-06 — Maintainability

The project structure shall support future extensions without requiring major changes to the existing codebase.

---

## 4. Technology Requirements

### Current

* Python
* JSON
* Git
* GitHub

### Planned

* PostgreSQL
* Docker
* Docker Compose
* Workflow orchestration
* REST APIs
* Cloud services
* Data processing technologies

The technology stack may evolve as the project progresses.

---

## 5. Project Evolution

The project is planned to evolve through the following stages:

```text
Local JSON ETL
      ↓
PostgreSQL
      ↓
External API
      ↓
Docker
      ↓
Workflow Orchestration
      ↓
Cloud Data Platform
```

Each stage should provide a working and testable increment rather than introducing multiple technologies simultaneously.

---

## 6. Definition of Done

A feature is considered complete when:

* The implementation is functional.
* Relevant validation is implemented.
* Errors are handled appropriately.
* Logging is available where required.
* Automated tests are added where appropriate.
* Documentation is updated.
* The code is committed to the repository.
