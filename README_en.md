# Mocap API Demo Collection

This project contains multiple demonstration programs based on `mocap_api` for interacting with various motion capture systems. These demos showcase how to use the `mocap_api` library to acquire motion capture data and send control commands.

## Demo Programs List

### 1. Axis Studio Command Control Demo (`mocap_axis_command_demo.py`)

**Function**: Used to control recording functions in Axis Studio software.

**Main Features**:
- Start/stop recording tasks
- Support for custom recording task names
- Command execution status checking
- Keyboard shortcut control

**Keyboard Shortcuts**:
- `N` - Set recording task name
- `R` - Start recording
- `S` - Stop recording
- `ESC` - Exit program

### 2. Axis Studio Data Receiving Demo (`mocap_axis_demo.py`)

**Function**: Real-time receive and display human body BVH data from Axis Studio.

**Main Features**:
- UDP protocol data reception
- Real-time parsing of human joint data
- Display joint names, positions, and rotation information

### 3. Hybrid Data Server Data Receiving Demo (`mocap_hds_demo.py`)

**Function**: Receive and display various data types from Hybrid Data Server.

**Supported Data Types**:
- Human body BVH data (`AvatarUpdated`)
- Tracker data (`AliceTrackerUpdated`)
- Marker scatter data (`AliceMarkerUpdated`)
- Rigid body data (`AliceRigidbodyUpdated`)
- Prop data (`TrackerUpdated`)
- Inertial sensor data (`AliceIMUUpdated`)

### 4. Axis Studio Calculation Data Receiving Demo (`mocap_axis_calc_demo.py`)

**Function**: Receive and display Calculation Data from Axis Studio.

**Main Features**:
- Configure Calculation Data reception
- Real-time parsing of bone sensor data
- Display posture, angular velocity, and acceleration information

### 5. PNLink Command Control Demo (`mocap_pnlink_command_demo.py`)

**Function**: Used to control various commands of PNLink devices.

**Supported Commands**:
- Start/stop capture (`N`/`F`)
- Motion calibration (`C`)
- Restore original hand posture (`R`)
- Clear zero motion drift (`0`)
- Restore original body posture (`O`)
- Reset position (`Z`)