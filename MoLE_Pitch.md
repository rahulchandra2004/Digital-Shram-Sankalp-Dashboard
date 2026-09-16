# MoLE Hackathon Submission: Digital Shram Sankalp
**Problem Statement 08 & 09: ML-Driven Data Quality and Real-Time Dashboards**

## 1. Relevance
The Ministry of Labour & Employment's eShram initiative aims to build a comprehensive national database of unorganized workers. However, database fragmentation, manual data entry errors, and disconnected state silos result in significant data quality challenges. Our solution directly tackles this by combining a real-time, self-cleaning Machine Learning pipeline with an intuitive Command Center dashboard. This ensures that policy decisions are driven by high-fidelity data, directly answering Problem Statements 08 and 09.

## 2. Innovation
The core innovation is our **Dual-Tier Deep Learning Architecture** integrated seamlessly into the ingestion layer:
1.  **Statistical Tier**: Uses an Isolation Forest algorithm to immediately flag structural outliers, providing a fast first line of defense.
2.  **Deep Learning Autoencoder Tier**: Rather than relying purely on static rules, we implemented a non-linear Autoencoder. This model learns the multi-dimensional structure of a "normal" worker profile (e.g., mapping expected wage bounds across specific skill and age clusters in particular destination states). High reconstruction errors instantly red-flag complex, fraudulent, or mathematically impossible records that simple scripts miss. 
*(Note: To ensure maximum feasibility and zero-dependency friction in highly restrictive Python 3.14 environments where native TensorFlow binaries are unavailable, the autoencoder mathematics are simulated using Scikit-Learn's MLPRegressor, achieving identical dimensionality reduction and anomaly detection logic).*

## 3. Feasibility
Designed for rapid deployment and massive scale, the solution is built on a highly portable Python stack (Streamlit, Pandas, Plotly, Scikit-Learn). 
-   **Low Overhead**: Streamlit allows for seamless deployment on standard government virtual machines without requiring complex, heavy frontend frameworks.
-   **Performant Processing**: Pandas easily scales to handle the 10,000-record synthetic benchmark and is engineered to adapt to direct API streams or SQL connections.
-   **Visual Impact**: The Plotly-powered dashboard translates complex Autoencoder output into a simple "Data Integrity Radar," allowing non-technical administrators to immediately comprehend and act upon flagged records.

## 4. Security
Data security is paramount when dealing with citizen records (UAN data).
-   **No Third-Party APIs**: The entire dual-tier machine learning pipeline runs entirely locally within the secure government perimeter. No data is sent to external LLMs or third-party cloud services for analysis.
-   **Data Masking Validation**: The pipeline inherently validates standard dummy formats (e.g., `MOCK-UAN-XXXX-1234`), providing an architectural blueprint for how PII (Personally Identifiable Information) masking can be rigorously enforced across all state nodes before data aggregation.

In summary, this prototype doesn't just display data; it cleans it, analyzes it using advanced Deep Learning heuristics, and transforms it into a strategic, secure asset for the empowerment of India's unorganized workforce.
