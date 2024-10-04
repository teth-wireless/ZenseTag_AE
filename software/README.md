
# Data Collection and Real Time Sensing

## Overview

This project provides scripts to collect and store RFID data using the `AntennaReader` class. It also provides scripts to show real-time phase on an User Interface using the `GUI` class. It connects to an Impinj RFID reader via the LLRP protocol and collects tag data for a specified duration. The collected data is processed and saved in different formats, including JSON and MATLAB `.mat` files.

## Prerequisites

### Hardware Requirements:
- Impinj RFID Reader
- Antennas connected to the RFID reader
- EPC-encoded RFID tags

### Software Requirements:
- Python 3.x
- Necessary Python packages:
  - `fastdtw`
  - `sllurp`
  - `scipy`
  - `json`
  - `datetime`
  - `os`

Make sure to install the required packages using:

```bash
pip install -r requirements.txt
```

## Project Structure

```
data_collection/
├── AntennaReader.py                  # Main class for connecting to the reader and collecting data
├── Gui.py                            # Main class for running the GUI
├── data_collection.py                # Script for executing data collection
├── real_time_phase_calculator.py     # Script for executing realtime gui
├── phase_calculation_functions.py    # Helper functions for calculating phase using sequence matching
├── params.py                         # Configuration file for sensors, RFID reader settings, etc.
├── rf_data_collection_functions.py   # Helper functions for processing collected data
├── README.md                         # This file
└── data/                             # Directory where collected data will be stored
```

## Usage

1. **Setting Up the Reader:**

   Before starting the data collection, set the sensor as well as configure the reader IP address and port in the `params.py` file:

   ```python
   IMPINJ_HOST_IP = "<your_reader_ip>"
   IMPINJ_HOST_PORT = 5084  # Default LLRP port
   SENSOR_DEF = "photo"
   ```

2. **Starting the Data Collection:**

   To start data collection, run the `data_collection.py` script from the command line with the desired file name and collection time.

   Example:
   
   ```bash
   python data_collection.py <file_name> <collection_time>
   ```

   - `<file_name>`: The base name for the data files that will be saved.
   - `<collection_time>`: The amount of time to collect data, specified in seconds (s), minutes (m), or hours (h).

   For example, to collect data for 5 minutes and save it with the base name `rfid_data`:

   ```bash
   python data_collection.py rfid_data 5m
   ```

   If no time is provided, the script defaults to collecting data for 10 seconds.

3. **Storing Data:**

   Data can be stored in multiple formats:
   
   - **Raw Data (JSON)**: Collected raw data is stored in the `data/rf_data/json/` directory. A timestamp is added to the filename.
   - **Channel-wise Data (JSON)**: Data organized by channel is stored in the `data/rf_data/json/` directory.
   - **MATLAB (.mat)**: The collected raw data is saved as `.mat` files in the `data/rf_data/matlab/` directory for further analysis.

   **Directory Structure:**
   
   - `data/rf_data/json`: Stores the JSON files containing the raw and channel-wise data.
   - `data/rf_data/matlab`: Stores the MATLAB `.mat` files containing the collected data.

   The filenames are automatically suffixed with a timestamp for easy reference.

4. **Real-time Data Collection (Optional):**

   To start real-time phase calculation, run the `real_time_phase_calculator.py` script from the command line with the desired file name

   Example:
   
   ```bash
   python real_time_phase_calculator.py <file_name>
   ```

   - `<file_name>`: The base name for the data files that will be saved.

## Example Workflow

1. Modify the `params.py` file to set up the correct sensor and RFID reader configurations.
   
   Example:
   ```python
   SENSOR_DEF = "photo"  # Select a sensor type
   ```

2. Run the data collection script:

   ```bash
   python data_collection.py test_data 10m
   ```

   This command will collect RFID data for 10 minutes and store the results in JSON and `.mat` formats.

3. Run the real-time phase GUI:

   ```bash
   python real_time_phase_calculator.py test_data
   ```

4. Verify the output data:

   The collected data will be available in the `data/rf_data/json` and `data/rf_data/matlab` directories.

## Functions Overview

### AntennaReader Class (in `AntennaReader.py`)
- `connect()`: Establishes a connection to the RFID reader.
- `startInventory()`: Starts inventorying tags from the connected reader.
- `disconnect()`: Disconnects from the reader and processes the collected data.
  
### Helper Functions (in `rf_data_collection_functions.py`)
- `get_raw_data_per_rf()`: Retrieves raw data per RF.
- `channel_wise_data_per_rf()`: Organizes raw data into a channel-wise structure.
- `store_raw_data_as_json()`: Saves the raw RFID data as a JSON file.
- `store_channelwise_data_as_json()`: Saves channel-wise RFID data as a JSON file.
- `store_raw_data_as_mat()`: Saves raw RFID data as a MATLAB `.mat` file.

---

## License

This project is open-source and available under the MIT License. Feel free to contribute!
