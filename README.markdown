# Stratified Sampling Framework

A Streamlit-based tool for creating a stratified sampling plan using the ADNKS 2023 dataset. The tool distributes a user-specified sample size across strata (Group × BŞ/M&D) and calculates the number of neighborhoods to sample.

## Setup

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd sampling-framework
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare Dataset**:
   - Place the `ADNKS 2023 Mahalle ve Köyler v01.xlsx` file in the project directory or upload it via the app.

4. **Run the App**:
   ```bash
   streamlit run main.py
   ```
   - Open the provided URL in a browser.

## Usage

1. **Upload Dataset**:
   - Upload the ADNKS dataset (Excel or CSV) via the web interface.

2. **Set Parameters**:
   - Enter the total sample size (e.g., 1000).
   - Specify the number of interviews per neighborhood (e.g., 10).

3. **Generate Sampling Plan**:
   - Click "Generate Sampling Plan" to view the sampling frame and plan.
   - The frame shows population distribution by stratum.
   - The plan includes sample sizes and neighborhood counts.

4. **Download Outputs**:
   - Go to the "Download Outputs" tab to preview and download a ZIP file containing:
     - `sampling_frame.xlsx`: Population by stratum.
     - `sampling_plan.xlsx`: Sample sizes and neighborhood counts.

## Project Structure

- `config.yaml`: Configuration for column mappings and stratum rules.
- `src/`
  - `data_loader.py`: Loads and preprocesses the dataset.
  - `sampling_frame.py`: Creates the sampling frame.
  - `sample_allocator.py`: Allocates samples and calculates neighborhoods.
  - `output_generator.py`: Generates output files.
  - `utils.py`: Utility functions for configuration and grouping.
  - `main.py`: Streamlit app.
- `requirements.txt`: Dependencies.
- `README.md`: This file.

## Notes

- The tool assumes the ADNKS dataset has columns like `NUTS1KODU`, `NUFUS2023`, etc., as specified in `config.yaml`.
- Special population adjustments are applied for Isparta (TR612) and Adıyaman (TRC13).
- Ensure `config.yaml` is in the project root directory.

## Future Enhancements

- Add neighborhood selection (Phase 2).
- Include visualizations (e.g., population distribution charts).
- Support custom stratum definitions via the UI.

## License

MIT License