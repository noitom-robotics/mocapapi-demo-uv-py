#include <MocapApi.h>
#include <windows.h>
#include <chrono>
#include <thread>
#include <windowsnumerics.h>
#include <timeapi.h>
#include <signal.h>
#include <iostream>
#include <fstream>
#include <ctime>
#include <format>
#include <sstream>
#include <iomanip>
#pragma comment( lib,"winmm.lib" )

using namespace MocapApi;
//服务IP地址
std::string strServerIP = "127.0.0.1";
//服务端口号
uint32_t strServerPort = 8001;
///输出到文件的buffer
bool bPrint2Buffer = false;
//输出缓冲区长度
size_t nBufferLen = 1024 * 200 * 1024;
//输出缓冲区首地址
char* logBuffer = nullptr;
//输出缓冲区首偏移
int logOffset = 0;

#define PrintInfo(format, ...) if (bPrint2Buffer){\
	logQuit();\
	logOffset += sprintf_s(logBuffer + logOffset, nBufferLen - logOffset, format, ##__VA_ARGS__);\
}\
else printf(format, ##__VA_ARGS__);

void logQuit()
{
    if (logOffset >= nBufferLen - 200) {
        std::ofstream outfile;
        outfile.open("./record.log");
        outfile << logBuffer;
        outfile.close();
        exit(1);
    }
}

/*
 *@brief:                           时间戳转日期
 *@param: uint64_t timestamp        接口接收到的时间戳
 *@return: void
 *@remark: 
 */
void printTimestamp(uint64_t timestamp)
{
    auto tp = std::chrono::time_point<std::chrono::system_clock, std::chrono::microseconds>(std::chrono::microseconds(timestamp));
    auto tt = std::chrono::system_clock::to_time_t(tp);
    std::tm* datetime = std::localtime(&tt);

    PrintInfo("%04d:%02d:%02d %02d:%02d:%02d.%06d\n"
        , datetime->tm_year + 1900
        , datetime->tm_mon + 1
        , datetime->tm_mday
        , datetime->tm_hour
        , datetime->tm_min
        , datetime->tm_sec
        , timestamp % 1000'000);
}

/*
 *@brief:                           printTimestamp升级版
 */
void printTimestampEx(uint64_t timestamp, const char* type, int32_t count)
{
    auto tp = std::chrono::time_point<std::chrono::system_clock, std::chrono::microseconds>(std::chrono::microseconds(timestamp));
    auto tt = std::chrono::system_clock::to_time_t(tp);
    std::tm* datetime = std::localtime(&tt);

    PrintInfo("%04d:%02d:%02d %02d:%02d:%02d.%06d\t"
        , datetime->tm_year + 1900
        , datetime->tm_mon + 1
        , datetime->tm_mday
        , datetime->tm_hour
        , datetime->tm_min
        , datetime->tm_sec
        , timestamp % 1000'000);

    PrintInfo("type: %s\t count:%d\n", type, count);
}

//骨骼节点定义
const char* tagnames[] = { 
    "JointTag_Hips"
    ,"JointTag_RightUpLeg"
    ,"JointTag_RightLeg"
    ,"JointTag_RightFoot"
    ,"JointTag_LeftUpLeg"
    ,"JointTag_LeftLeg"
    ,"JointTag_LeftFoot"
    ,"JointTag_Spine"
    ,"JointTag_Spine1"
    ,"JointTag_Spine2"
    ,"JointTag_Neck"
    ,"JointTag_Neck1"
    ,"JointTag_Head"
    ,"JointTag_RightShoulder"
    ,"JointTag_RightArm"
    ,"JointTag_RightForeArm"
    ,"JointTag_RightHand"
    ,"JointTag_RightHandThumb1"
    ,"JointTag_RightHandThumb2"
    ,"JointTag_RightHandThumb3"
    ,"JointTag_RightInHandIndex"
    ,"JointTag_RightHandIndex1"
    ,"JointTag_RightHandIndex2"
    ,"JointTag_RightHandIndex3"
    ,"JointTag_RightInHandMiddle"
    ,"JointTag_RightHandMiddle1"
    ,"JointTag_RightHandMiddle2"
    ,"JointTag_RightHandMiddle3"
    ,"JointTag_RightInHandRing"
    ,"JointTag_RightHandRing1"
    ,"JointTag_RightHandRing2"
    ,"JointTag_RightHandRing3"
    ,"JointTag_RightInHandPinky"
    ,"JointTag_RightHandPinky1"
    ,"JointTag_RightHandPinky2"
    ,"JointTag_RightHandPinky3"
    ,"JointTag_LeftShoulder"
    ,"JointTag_LeftArm"
    ,"JointTag_LeftForeArm"
    ,"JointTag_LeftHand"
    ,"JointTag_LeftHandThumb1"
    ,"JointTag_LeftHandThumb2"
    ,"JointTag_LeftHandThumb3"
    ,"JointTag_LeftInHandIndex"
    ,"JointTag_LeftHandIndex1"
    ,"JointTag_LeftHandIndex2"
    ,"JointTag_LeftHandIndex3"
    ,"JointTag_LeftInHandMiddle"
    ,"JointTag_LeftHandMiddle1"
    ,"JointTag_LeftHandMiddle2"
    ,"JointTag_LeftHandMiddle3"
    ,"JointTag_LeftInHandRing"
    ,"JointTag_LeftHandRing1"
    ,"JointTag_LeftHandRing2"
    ,"JointTag_LeftHandRing3"
    ,"JointTag_LeftInHandPinky"
    ,"JointTag_LeftHandPinky1"
    ,"JointTag_LeftHandPinky2"
    ,"JointTag_LeftHandPinky3"
    ,"JointTag_JointsCount"
};

const char retarget[] = {
    R"(
{
    "ankelHeight": 0.0,
    "ankelOrder": {
        "axis1": 1,
        "axis2": 0,
        "axis3": 2
    },
    "headOrder": {
        "axis1": 2,
        "axis2": 0,
        "axis3": 1
    },
    "hipOrder": {
        "axis1": 2,
        "axis2": 1,
        "axis3": 0
    },
    "lowerBodyHeight": 0.0,
    "lowerBodyMode": 0,
    "lowerLegLength": 0.0,
    "retargetJoints": [
        {
            "max": 6.283199787139893,
            "maxSpeed": 5.099999904632568,
            "min": -6.283199787139893,
            "offset": 90.0,
            "rawJoint": 9,
            "retargetJoint": "r-j3",
            "sign": 1
        },
        {
            "max": 0.5235000252723694,
            "maxSpeed": 5.099999904632568,
            "min": -2.5306999683380127,
            "offset": 0.0,
            "rawJoint": 10,
            "retargetJoint": "r-j4",
            "sign": -1
        },
        {
            "max": 1.8324999809265137,
            "maxSpeed": 2.0999999046325684,
            "min": -1.8324999809265137,
            "offset": 0.0,
            "rawJoint": 12,
            "retargetJoint": "r-j6",
            "sign": 1
        },
        {
            "max": 6.283199787139893,
            "maxSpeed": 2.0999999046325684,
            "min": -6.283199787139893,
            "offset": 90.0,
            "rawJoint": 11,
            "retargetJoint": "r-j5",
            "sign": 1
        },
        {
            "max": 1.7000000476837158,
            "maxSpeed": 5.099999904632568,
            "min": 0.0,
            "offset": 0.0,
            "rawJoint": 52,
            "retargetJoint": "R_index_MCP_joint",
            "sign": 1
        },
        {
            "max": 1.600000023841858,
            "maxSpeed": 5.099999904632568,
            "min": 0.0,
            "offset": 0.0,
            "rawJoint": 53,
            "retargetJoint": "R_index_DIP_joint",
            "sign": 1
        },
        {
            "max": 1.7000000476837158,
            "maxSpeed": 5.099999904632568,
            "min": 0.0,
            "offset": 0.0,
            "rawJoint": 55,
            "retargetJoint": "R_middle_MCP_joint",
            "sign": 1
        },
        {
            "max": 1.600000023841858,
            "maxSpeed": 5.099999904632568,
            "min": 0.0,
            "offset": 0.0,
            "rawJoint": 56,
            "retargetJoint": "R_middle_DIP_joint",
            "sign": 1
        },
        {
            "max": 1.7000000476837158,
            "maxSpeed": 5.099999904632568,
            "min": 0.0,
            "offset": 0.0,
            "rawJoint": 58,
            "retargetJoint": "R_ring_MCP_joint",
            "sign": 1
        },
        {
            "max": 1.600000023841858,
            "maxSpeed": 5.099999904632568,
            "min": 0.0,
            "offset": 0.0,
            "rawJoint": 59,
            "retargetJoint": "R_ring_DIP_joint",
            "sign": 1
        },
        {
            "max": 1.7000000476837158,
            "maxSpeed": 5.099999904632568,
            "min": 0.0,
            "offset": 0.0,
            "rawJoint": 61,
            "retargetJoint": "R_pinky_MCP_joint",
            "sign": 1
        },
        {
            "max": 1.600000023841858,
            "maxSpeed": 5.099999904632568,
            "min": 0.0,
            "offset": 0.0,
            "rawJoint": 62,
            "retargetJoint": "R_pinky_DIP_joint",
            "sign": 1
        },
        {
            "max": 1.0,
            "maxSpeed": 5.099999904632568,
            "min": 0.0,
            "offset": 0.0,
            "rawJoint": 50,
            "retargetJoint": "R_thumb_PIP_joint",
            "sign": 1
        },
        {
            "max": 0.699999988079071,
            "maxSpeed": 5.099999904632568,
            "min": 0.0,
            "offset": 0.0,
            "rawJoint": 51,
            "retargetJoint": "R_thumb_DIP_joint",
            "sign": 1
        },
        {
            "max": 1.5,
            "maxSpeed": 5.099999904632568,
            "min": 0.20000000298023224,
            "offset": -60.0,
            "rawJoint": 48,
            "retargetJoint": "R_thumb_MCP_joint1",
            "sign": 1
        },
        {
            "max": 6.283199787139893,
            "maxSpeed": 5.099999904632568,
            "min": -6.283199787139893,
            "offset": 0.0,
            "rawJoint": 0,
            "retargetJoint": "l-j1",
            "sign": 1
        },
        {
            "max": 1.8324999809265137,
            "maxSpeed": 5.099999904632568,
            "min": -1.8324999809265137,
            "offset": -90.0,
            "rawJoint": 1,
            "retargetJoint": "l-j2",
            "sign": 1
        },
        {
            "max": 6.283199787139893,
            "maxSpeed": 5.099999904632568,
            "min": -6.283199787139893,
            "offset": -90.0,
            "rawJoint": 2,
            "retargetJoint": "l-j3",
            "sign": 1
        },
        {
            "max": 0.5235000252723694,
            "maxSpeed": 5.099999904632568,
            "min": -2.5306999683380127,
            "offset": 0.0,
            "rawJoint": 3,
            "retargetJoint": "l-j4",
            "sign": -1
        },
        {
            "max": 6.283199787139893,
            "maxSpeed": 2.0999999046325684,
            "min": -6.283199787139893,
            "offset": -90.0,
            "rawJoint": 4,
            "retargetJoint": "l-j5",
            "sign": 1
        },
        {
            "max": 1.8324999809265137,
            "maxSpeed": 2.0999999046325684,
            "min": -1.8324999809265137,
            "offset": 0.0,
            "rawJoint": 5,
            "retargetJoint": "l-j6",
            "sign": 1
        },
        {
            "max": 1.100000023841858,
            "maxSpeed": 5.099999904632568,
            "min": 0.0,
            "offset": -45.0,
            "rawJoint": 32,
            "retargetJoint": "L_thumb_MCP_joint1",
            "sign": 1
        },
        {
            "max": 1.0,
            "maxSpeed": 5.099999904632568,
            "min": 0.0,
            "offset": 0.0,
            "rawJoint": 34,
            "retargetJoint": "L_thumb_PIP_joint",
            "sign": 1
        },
        {
            "max": 1.2000000476837158,
            "maxSpeed": 5.099999904632568,
            "min": 0.0,
            "offset": 0.0,
            "rawJoint": 35,
            "retargetJoint": "L_thumb_DIP_joint",
            "sign": 1
        },
        {
            "max": 1.7000000476837158,
            "maxSpeed": 5.099999904632568,
            "min": 0.0,
            "offset": 0.0,
            "rawJoint": 36,
            "retargetJoint": "L_index_MCP_joint",
            "sign": 1
        },
        {
            "max": 1.600000023841858,
            "maxSpeed": 5.099999904632568,
            "min": 0.0,
            "offset": 0.0,
            "rawJoint": 37,
            "retargetJoint": "L_index_DIP_joint",
            "sign": 1
        },
        {
            "max": 1.7000000476837158,
            "maxSpeed": 5.099999904632568,
            "min": 0.0,
            "offset": 0.0,
            "rawJoint": 39,
            "retargetJoint": "L_middle_MCP_joint",
            "sign": 1
        },
        {
            "max": 1.600000023841858,
            "maxSpeed": 5.099999904632568,
            "min": 0.0,
            "offset": 0.0,
            "rawJoint": 40,
            "retargetJoint": "L_middle_DIP_joint",
            "sign": 1
        },
        {
            "max": 1.7000000476837158,
            "maxSpeed": 5.099999904632568,
            "min": 0.0,
            "offset": 0.0,
            "rawJoint": 42,
            "retargetJoint": "L_ring_MCP_joint",
            "sign": 1
        },
        {
            "max": 1.600000023841858,
            "maxSpeed": 5.099999904632568,
            "min": 0.0,
            "offset": 0.0,
            "rawJoint": 43,
            "retargetJoint": "L_ring_DIP_joint",
            "sign": 1
        },
        {
            "max": 1.7000000476837158,
            "maxSpeed": 5.099999904632568,
            "min": 0.0,
            "offset": 0.0,
            "rawJoint": 45,
            "retargetJoint": "L_pinky_MCP_joint",
            "sign": 1
        },
        {
            "max": 1.600000023841858,
            "maxSpeed": 5.099999904632568,
            "min": 0.0,
            "offset": 0.0,
            "rawJoint": 46,
            "retargetJoint": "L_pinky_DIP_joint",
            "sign": 1
        },
        {
            "max": 0.699999988079071,
            "maxSpeed": 5.099999904632568,
            "min": 0.0,
            "offset": 45.0,
            "rawJoint": 49,
            "retargetJoint": "R_thumb_MCP_joint2",
            "sign": 1
        },
        {
            "max": 6.283199787139893,
            "maxSpeed": 2.015927791595459,
            "min": -6.283199787139893,
            "offset": 90.0,
            "rawJoint": 6,
            "retargetJoint": "l-j7",
            "sign": 1
        },
        {
            "max": 0.5,
            "maxSpeed": 5.099999904632568,
            "min": 0.0,
            "offset": 0.0,
            "rawJoint": 33,
            "retargetJoint": "L_thumb_MCP_joint2",
            "sign": 1
        },
        {
            "max": 6.283199787139893,
            "maxSpeed": 2.015927791595459,
            "min": -6.283199787139893,
            "offset": -90.0,
            "rawJoint": 13,
            "retargetJoint": "r-j7",
            "sign": -1
        },
        {
            "max": 1.8324999809265137,
            "maxSpeed": 5.099999904632568,
            "min": -1.8324999809265137,
            "offset": -90.0,
            "rawJoint": 8,
            "retargetJoint": "r-j2",
            "sign": -1
        },
        {
            "max": 6.283199787139893,
            "maxSpeed": 5.099999904632568,
            "min": -6.283199787139893,
            "offset": 0.0,
            "rawJoint": 7,
            "retargetJoint": "r-j1",
            "sign": 1
        }
    ],
    "shoulderAngle": 0.0,
    "shoulderOrder": {
        "axis1": 1,
        "axis2": 0,
        "axis3": 2
    },
    "spineOrder": {
        "axis1": 2,
        "axis2": 0,
        "axis3": 1
    },
    "upperLegLength": 0.0,
    "urdfJointNames": [
        "r-j1",
        "r-j2",
        "r-j3",
        "r-j4",
        "r-j5",
        "r-j6",
        "r-j7",
        "L_thumb_MCP_joint1",
        "L_thumb_MCP_joint2",
        "L_thumb_PIP_joint",
        "L_thumb_DIP_joint",
        "L_index_MCP_joint",
        "L_index_DIP_joint",
        "L_middle_MCP_joint",
        "L_middle_DIP_joint",
        "L_ring_MCP_joint",
        "L_ring_DIP_joint",
        "L_pinky_MCP_joint",
        "L_pinky_DIP_joint",
        "l-j1",
        "l-j2",
        "l-j3",
        "l-j4",
        "l-j5",
        "l-j6",
        "l-j7",
        "R_thumb_MCP_joint1",
        "R_thumb_MCP_joint2",
        "R_thumb_PIP_joint",
        "R_thumb_DIP_joint",
        "R_index_MCP_joint",
        "R_index_DIP_joint",
        "R_middle_MCP_joint",
        "R_middle_DIP_joint",
        "R_ring_MCP_joint",
        "R_ring_DIP_joint",
        "R_pinky_MCP_joint",
        "R_pinky_DIP_joint"
    ],
    "useAngleLimit": true,
    "useSpeedLimit": true,
    "wristOrder": {
        "axis1": 1,
        "axis2": 0,
        "axis3": 1
    }
}
)"
};

//全局错误码
EMCPError error = EMCPError::Error_None;
//全局定义App接口及句柄
IMCPApplication* pGlobalApp = nullptr;
MCPApplicationHandle_t globalAppHandle = 0;
//全局定义设置接口及句柄
IMCPSettings* pGlobalSetting = nullptr;
MCPSettingsHandle_t globalSettingHandle = 0;
//#ifdef _SUPORT_ALICE_NEW_
//Alice 数据分发
IMCPAliceHub* pAliceDataHub = nullptr;
MCPAliceBusHandle_t aliceBusHandle = 0;
//#endif
//人物接收接口及句柄
IMCPAvatar* pAvatarInterface = nullptr;
MCPAvatarHandle_t avatarHandle = 0;
//Device接收接口及句柄
IMCPTracker* pDeviceInterface = nullptr;
MCPTrackerHandle_t deviceHandle = 0;
//IMU接收接口及句柄
IMCPSensorModule* pImuInterface = nullptr;
MCPSensorModuleHandle_t imuHandle = 0;
//#ifdef _SUPORT_ALICE_NEW_
//Marker接收接口及句柄
IMCPMarker* pMarkerInterface = nullptr;
MCPMarkerHandle_t markerHandle = 0;
//#endif
//刚体接收接口及句柄
IMCPRigidBody* pRigidbodyInterface = nullptr;
MCPRigidBodyHandle_t rigidbodyHandle = 0;
//#ifdef _SUPORT_ALICE_NEW_
//Tracker/PWR接收接口及句柄
IMCPPWR* pPWRInterface = nullptr;
MCPPWRHandle_t pwrHandle = 0;
//#endif
//渲染相关的接口及句柄
IMCPRenderSettings* pRenderSetting = nullptr;
MCPRenderSettingsHandle_t renderSettingHandle = 0;

//最多事件数量
static constexpr uint32_t nMaxEventCount = 16;
//接收事件
MCPEvent_t pEvents[nMaxEventCount] = {};
//当前批次事件数量
uint32_t nEventCount = 0;
//人物关节句柄
MCPJointHandle_t joint = 0;
//全身关节句柄
MCPJointHandle_t alljoint[59] = {};

//机器人接口
IMCPRobot* robotInterface = nullptr;


int setMCPSettings(IMCPSettings* setting, MCPSettingsHandle_t handle) {
    if (setting == nullptr || handle == 0)
    {
        return 1;
    }

    error = setting->SetSettingsBvhData(BvhDataType_Binary, handle);
    error = setting->SetSettingsBvhRotation(BvhRotation_YXZ, handle);
    error = setting->SetSettingsBvhTransformation(BvhTransformation_Disable, handle);
    error = setting->SetSettingsTCP(strServerIP.c_str(), strServerPort, handle);
    //error = setting->SetSettingsUDPServer(strServerIP.c_str(), strServerPort, handle);
   // error = setting->SetSettingsUDP(8002, handle);
    return 0;
}

void setup()
{
    //创建并初始化全局App接口
    error = MCPGetGenericInterface(IMCPApplication_Version, reinterpret_cast<void**>(&pGlobalApp));
    error = pGlobalApp->CreateApplication(&globalAppHandle);
    //创建并初始化全局设置接口
    MocapApi::MCPGetGenericInterface(IMCPSettings_Version, reinterpret_cast<void**>(&pGlobalSetting));
    pGlobalSetting->CreateSettings(&globalSettingHandle);
    int result = setMCPSettings(pGlobalSetting, globalSettingHandle);
    //激活设置并销毁不再需要的设置
    error = pGlobalApp->SetApplicationSettings(globalSettingHandle, globalAppHandle);
    error = pGlobalSetting->DestroySettings(globalSettingHandle);

    //添加各种数据接收接口的关联
    error = MCPGetGenericInterface(IMCPAvatar_Version, reinterpret_cast<void**>(&pAvatarInterface));
    error = MCPGetGenericInterface(IMCPSensorModule_Version, reinterpret_cast<void**>(&pImuInterface));
//#ifdef _SUPORT_ALICE_NEW_
    error = MCPGetGenericInterface(IMCPMarker_Version, reinterpret_cast<void**>(&pMarkerInterface));
//#endif
    error = MCPGetGenericInterface(IMCPRigidBody_Version, reinterpret_cast<void**>(&pRigidbodyInterface));     //注意这里选的是Rigidbody协议2
//#ifdef _SUPORT_ALICE_NEW_
    error = MCPGetGenericInterface(IMCPPWR_Version, reinterpret_cast<void**>(&pPWRInterface));
    error = MCPGetGenericInterface(IMCPAliceHub_Version, reinterpret_cast<void**>(&pAliceDataHub));
//#endif
    error = MCPGetGenericInterface(IMCPTracker_Version, reinterpret_cast<void**>(&pDeviceInterface));

    for (uint32_t i = 0; i < nMaxEventCount; i++) {
        pEvents[i].size = sizeof(MCPEvent_t);
    }

    //创建并初始化渲染相关的接口
    error = MCPGetGenericInterface(IMCPRenderSettings_Version, reinterpret_cast<void**>(&pRenderSetting));
    pRenderSetting->GetPreDefRenderSettings(PreDefinedRenderSettings_Default, &renderSettingHandle);
    pGlobalApp->SetApplicationRenderSettings(renderSettingHandle, globalAppHandle);

    //Go
    error = pGlobalApp->OpenApplication(globalAppHandle);
}

void destroy()
{
    error = pGlobalApp->CloseApplication(globalAppHandle);
    error = pGlobalApp->DestroyApplication(globalAppHandle);
}

void updateJoints(MCPJointHandle_t joint, MCPAvatarHandle_t avatar)
{
    MocapApi::IMCPJoint* jointMgr = nullptr;
    MocapApi::MCPGetGenericInterface(MocapApi::IMCPJoint_Version, (void**)&jointMgr);

    const char* name = nullptr;
    error = jointMgr->GetJointName(&name, joint);
    MCPJointHandle_t tmpjoint = 0;
    pAvatarInterface->GetAvatarJointByName(name, &tmpjoint, avatar);
    Windows::Foundation::Numerics::float3 p;
    Windows::Foundation::Numerics::float4 r;
    MCPJointHandle_t childjoints[5];
    EMCPJointTag jointtags[5];
    uint32_t numberOfChildren = 0;
    EMCPJointTag jointT;
    if (joint) {
        error = jointMgr->GetJointLocalRotation(&r.x, &r.y, &r.z, &r.w, joint);
        error = jointMgr->GetJointLocalPosition(&p.x, &p.y, &p.z, joint);
        if (error != Error_None)        //这里用来规避勾选“不带位移”后仍调用该接口所产生的野值
        {
            p.x = p.y = p.z = 0;
        }
        error = jointMgr->GetJointTag(&jointT, joint);

		PrintInfo("JointName:%s  JointTag<%d>:%s \n    pos:(%f, %f, %f)   quat(%f, %f, %f, %f)\n"
        , name, jointT, tagnames[jointT], p.x, p.y, p.z, r.w, r.x, r.y, r.z);

        error = jointMgr->GetJointLocalRotationByEuler(&p.x, &p.y, &p.z, joint);

		PrintInfo("    eular:(%f, %f, %f)\n", p.x, p.y, p.z);

        const char* tmpname = nullptr;
        error = jointMgr->GetJointNameByTag(&tmpname, jointT);
        EMCPJointTag tmpjointT;
        error = jointMgr->GetJointParentJointTag(&tmpjointT, jointT);
        error = jointMgr->GetJointChild(nullptr, &numberOfChildren, joint);

        if (numberOfChildren > 0) {
            error = jointMgr->GetJointChild(childjoints, &numberOfChildren, joint);
            for (uint32_t j = 0; j < numberOfChildren; j++) {
                updateJoints(childjoints[j], avatar);
            }
        }
    }
    return;
}

void FrameTime()
{
    auto now = std::chrono::system_clock::now();
    std::time_t timestamp_seconds = std::chrono::system_clock::to_time_t(now);
    auto milliseconds = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()) % 1000;
    std::tm* timeinfo = std::localtime(&timestamp_seconds);
    std::stringstream ss;
    ss << std::put_time(timeinfo, "%Y-%m-%d %H:%M:%S") << '.' << std::setfill('0') << std::setw(3) << milliseconds.count();
    std::string timeStr = ss.str();
    PrintInfo("Frame Time: %s\n" , timeStr.c_str());
     
}


int main(int argc, char** argv)
{
    if (argc > 1) strServerIP = argv[1];
    if (argc > 2) strServerPort = atoi(argv[2]);
    if (argc > 3) {
        bPrint2Buffer = true;
        nBufferLen = max(1, atoi(argv[3])) * 1024;
        logBuffer = new char[nBufferLen];
    }

   


    printf("***MocapAPI***\n");
    printf("Server ip: %s    Server port: %d\n", strServerIP.c_str(), strServerPort);
    setup();

    //免得每次都要构造和析构，提前定义一点变量
    uint32_t size;
    int32_t indexes[1024];
    float pos[3], acce[3], gyro[3], quat[4], axisAngle[4];
    int32_t itemsCount;
    uint64_t timestamp;
    uint32_t count;
    uint32_t id;
    int id2, status;


    time_t  now = time(0);          //当前系统时间精确到秒
    tm* gm = localtime(&now);       //转为gmt时间
    time_t utc = mktime(gm);        //gmt对应的时间戳

    int64_t time = utc - now;       //秒级时区转化
    uint64_t baseTime = time * 1e3;

    ////根据版本获取机器人接口
    //EMCPError robotError=  MCPGetGenericInterface(IMCPRobot_Version,(void**)&robotInterface);
   
    //    MCPRobotHandle_t pHandle = 0;
    //    //创建一个机器人
    //    robotInterface->CreateRobot(retarget, &pHandle);
    //    int fps = 100;
    //    //输入数据帧数
    //    robotInterface->SetRobotFPS(fps, pHandle);



    bool isListening = true;
    while (isListening) {
        nEventCount = 0;
        error = pGlobalApp->PollApplicationNextEvent(nullptr, &nEventCount, globalAppHandle);
        if (nEventCount) {
            error = pGlobalApp->PollApplicationNextEvent(pEvents, &nEventCount, globalAppHandle);
            for (uint32_t i = 0; i < nEventCount; i++) {


                if (pEvents[i].eventType == MCPEvent_AvatarUpdated)
                {
                    FrameTime();

                    avatarHandle = pEvents[i].eventData.motionData.avatarHandle;
                    const char* tmpName = nullptr;
                    error = pAvatarInterface->GetAvatarRootJoint(&joint, avatarHandle);
                    error = pAvatarInterface->GetAvatarName(&tmpName, avatarHandle);

                    PrintInfo("AvatarName: %s\n", tmpName);
                    uint32_t jointSize = 0;
                    error = pAvatarInterface->GetAvatarJoints(nullptr, &jointSize, avatarHandle);
                    error = pAvatarInterface->GetAvatarJoints(alljoint, &jointSize, avatarHandle);
                    MCPJointHandle_t jointHandle = 0;
                    error = pAvatarInterface->GetAvatarJointByName("Hips", &jointHandle, avatarHandle);
                    if (error == Error_None && jointSize > 0)
                    {
                        updateJoints(jointHandle, avatarHandle);
                    }

                    ////每帧获取机器人的关节数据
                    //robotInterface->UpdateRobot(avatarHandle, pHandle);
                    //Windows::Foundation::Numerics::float3 p;
                    //Windows::Foundation::Numerics::float4 r;
                    ////root节点数据
                    //robotInterface->GetRobotRootPosition(&p.x, &p.y, &p.z, pHandle);
                    //robotInterface->GetRobotRootRotation(&r.x, &r.y, &r.z, &r.w, pHandle);

                    //PrintInfo("RobotRoot: pos:(%f, %f, %f)   quat(%f, %f, %f, %f)\n", p.x, p.y, p.z, r.w, r.x, r.y, r.z);

                    ////jointName为此retarget的具体关节节点，可根据需求输入，调用后返回一个角度。
                    //char* jointName = "r-j1";
                    //float value = 0;
                    //robotInterface->GetRobotRetargetJointAngle(jointName, &value, pHandle);
                    //PrintInfo("RobotjointName:%s :%f  \n", jointName,value);
                    ////获取jsonStr
                    //bool compress = true;
                    //const char* result;
                    //EMCPError robotStatus = robotInterface->GetRobotRosFrameJson(&result, compress, pHandle);
                    //if (robotStatus == Error_None)
                    //{
                    //    PrintInfo("jsonStr: %s  \n", result);
                    //}
                    //else
                    //{
                    //}
                    //robotInterface->RunRobotStep(pHandle);

                }
//#ifdef _SUPORT_ALICE_NEW_
                else if (pEvents[i].eventType == MCPEvent_AliceMarkerUpdated)
                {

                    pAliceDataHub->GetMarkerList(nullptr, &count);                  //第一次传入参1为nullptr，意为获取对象的数量
                    if (count > 0)
                    {
                        FrameTime();
                        MCPMarkerHandle_t* recv = new MCPMarkerHandle_t[count];     //动态开辟接收内存
                        pAliceDataHub->GetMarkerList(recv, &count);                 //第二次传入参1不为nullptr，将接收实际的handle列表
                        pAliceDataHub->GetMarkerTimestamp(&timestamp);              //以包为单位的时间戳

                        printTimestampEx(timestamp, "Marker", count);
                        for (size_t i = 0; i < count; ++i)
                        {
                            pMarkerInterface->GetMarkerPosition(&pos[0], &pos[1], &pos[2], recv[i]);
                            PrintInfo("marker:(%f, %f, %f)\n"
                                , pos[0], pos[1], pos[2]);
                        }

                        delete[] recv;
                        recv = nullptr;
                    }
                }
                else if (pEvents[i].eventType == MCPEvent_AliceIMUUpdated)
                {
                    //详见 MCPEvent_AliceMarkerUpdated 类型事件接收的注释
                    pAliceDataHub->GetSensorModuleList(nullptr, &count);
                    if (count > 0)
                    {
                        //时间戳
                        FrameTime();

                        MCPSensorModuleHandle_t* recv = new MCPSensorModuleHandle_t[count];
                        pAliceDataHub->GetSensorModuleList(recv, &count);
                        pAliceDataHub->GetSensorModuleTimestamp(&timestamp);

                        printTimestampEx(timestamp, "IMU", count);
                        for (size_t i = 0; i < count; ++i)
                        {
                            pImuInterface->GetSensorModuleId(&id, recv[i]);
                            pImuInterface->GetSensorModuleAcceleratedVelocity(&acce[0], &acce[1], &acce[2], recv[i]);
                            pImuInterface->GetSensorModuleAngularVelocity(&gyro[0], &gyro[1], &gyro[2], recv[i]);
                            pImuInterface->GetSensorModulePosture(&quat[0], &quat[1], &quat[2], &quat[3], recv[i]);
                            PrintInfo("id:(%d), accelerometer:(%f, %f, %f), gyroscope:(%f, %f, %f), quat:(%f, %f, %f, %f)\n"
                                , id
                                , acce[0], acce[1], acce[2]
                                , gyro[0], gyro[1], gyro[2]
                                , quat[0], quat[1], quat[2], quat[3]);
                        }
                        delete[] recv;
                        recv = nullptr;
                    }
                }
				else if (pEvents[i].eventType == MCPEvent_AliceRigidbodyUpdated)
				{
                    //详见 MCPEvent_AliceMarkerUpdated 类型事件接收的注释
                    pAliceDataHub->GetRigidBodyList(nullptr, &count);
                    if (count > 0)
                    {
                        //时间戳
                        FrameTime();

                        MCPRigidBodyHandle_t* recv = new MCPRigidBodyHandle_t[count];
                        pAliceDataHub->GetRigidBodyList(recv, &count);
                        pAliceDataHub->GetRigidBodyTimestamp(&timestamp);

                        printTimestampEx(timestamp, "Rigid body", count);
                        for (size_t i = 0; i < count; ++i)
                        {
                            pRigidbodyInterface->GetRigidBodyId(&id2, recv[i]);
                            pRigidbodyInterface->GetRigidBodyPosition(&pos[0], &pos[1], &pos[2], recv[i]);
                            pRigidbodyInterface->GetRigidBodyRotation(&quat[0], &quat[1], &quat[2], &quat[3], recv[i]);
                            pRigidbodyInterface->GetRigidBodyAxisAngle(&axisAngle[0], &axisAngle[1], &axisAngle[2], &axisAngle[3], recv[i]);
                            PrintInfo("id:(%d), pos:(%f, %f, %f), quat:(%f, %f, %f, %f(w))\naxisAngle:((%f, %f, %f), %f)\n"
                                , id2
                                , pos[0], pos[1], pos[2]
                                , quat[0], quat[1], quat[2], quat[3]
                                , axisAngle[0], axisAngle[1], axisAngle[2], axisAngle[3]);
                        }
                        delete[] recv;
                        recv = nullptr;
                    }
				}
                else if (pEvents[i].eventType == MCPEvent_AliceTrackerUpdated)
                {
                    //详见 MCPEvent_AliceMarkerUpdated 类型事件接收的注释
                    pAliceDataHub->GetPWRList(nullptr, &count);
                    if (count > 0)
                    {
                        //时间戳
                        FrameTime();

                        MCPPWRHandle_t* recv = new MCPPWRHandle_t[count];
                        pAliceDataHub->GetPWRList(recv, &count);
                        pAliceDataHub->GetPWRTimestamp(&timestamp);

                        printTimestampEx(timestamp, "Tracker", count);

                        for (size_t i = 0; i < count; ++i)
                        {
                            pPWRInterface->GetPWRId(&id, recv[i]);
                            pPWRInterface->GetPWRStatus(&status, recv[i]);
                            pPWRInterface->GetPWRPosition(&pos[0], &pos[1], &pos[2], recv[i]);
                            pPWRInterface->GetPWRQuaternion(&quat[0], &quat[1], &quat[2], &quat[3], recv[i]);
                            PrintInfo("id:(%d), status(%d), pos:(%f, %f, %f), quat:(%f, %f, %f, %f)\n"
                                , id, status
                                , pos[0], pos[1], pos[2]
                                , quat[0], quat[1], quat[2], quat[3]);
                        }

                        delete[] recv;
                        recv = nullptr;
                    }
                }
//#endif
                else if (pEvents[i].eventType == MCPEvent_TrackerUpdated)
                {
                    //时间戳
                    FrameTime();

                    deviceHandle = pEvents[i].eventData.trackerData._trackerHandle;
                    int count = 0; 
                    pDeviceInterface->GetDeviceCount(&count, deviceHandle);

                    auto tp = std::chrono::time_point_cast<std::chrono::milliseconds>(std::chrono::system_clock::now());
                    PrintInfo("[Device Timestamp]%lld\n", std::chrono::duration_cast<std::chrono::milliseconds>(tp.time_since_epoch()).count() + baseTime);
                    for (int i = 0; i < count; ++i)
                    {
                        const char* name;//这里无需开辟内存
                        pDeviceInterface->GetDeviceName(i, &name, deviceHandle);
                        pDeviceInterface->GetTrackerPosition(&pos[0], &pos[1], &pos[2], name, deviceHandle);
                        pDeviceInterface->GetTrackerRotation(&quat[0], &quat[1], &quat[2], &quat[3], name, deviceHandle);

                        PrintInfo("[Device]name:(%s), pos:(%f, %f, %f), quat:(%f, %f, %f, %f)\n"
                            , name
                            , pos[0], pos[1], pos[2]
                            , quat[0], quat[1], quat[2], quat[3]);
                    }
                }
            }
//             if (nEventCount == 0) {
//                 auto tp = std::chrono::time_point_cast<std::chrono::milliseconds>(std::chrono::system_clock::now());
//                 PrintInfo("[None Message]%lld\n", std::chrono::duration_cast<std::chrono::milliseconds>(tp.time_since_epoch()).count() + baseTime);
//             }
        }
    }

  
  //  robotInterface->DestroyRobot(pHandle);

    destroy();
    return 0;
}