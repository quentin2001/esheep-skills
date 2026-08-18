# Local Compute Capability Detection & ASR Model Matching Guide (本地算力探测与模型匹配指南)

This guide provides practical detection commands, hardware thresholds, and decision logic for AI agents to assess local compute capabilities and route between **SenseVoiceSmall (Local 220MB)** and **Cloud ASR API**.

---

## 1. Hardware Detection (硬件探测)

AI agents can run:
```bash
python scripts/asr_engine.py --probe-hardware
```

Output:
```json
{
  "has_gpu": true,
  "gpu_info": "NVIDIA GeForce RTX 3070, 8192 MiB",
  "recommended_local_engine": "SenseVoiceSmall (220MB)",
  "can_run_local": true
}
```

---

## 2. Model Tier & Hardware Recommendation (推荐方案表)

| Hardware Environment | Recommended Local Model | Download Size | Speed Estimate | Notes |
|---|---|---|---|---|
| **NVIDIA GPU (VRAM ≥ 2GB)** | **SenseVoiceSmall** | **~220 MB** | **~100x – 300x 实时** | 极速秒转，自带标点与情感/BGM识别 |
| **Apple Silicon (M1/M2/M3/M4)** | **SenseVoiceSmall** | **~220 MB** | **~30x – 60x 实时** | MPS 统一内存加速 |
| **Pure CPU (Intel / AMD)** | **SenseVoiceSmall** or Cloud API | **~220 MB** | **~5x – 10x 实时** | 220MB 极小，轻薄本 CPU 亦可轻松运行；长音频建议使用云端 API |

---

## 3. Decision Logic Tree (决策逻辑树)

```text
User triggers media transcription
├── Local GPU Available (NVIDIA CUDA / Apple Silicon MPS)?
│   ├── YES → Default to Local SenseVoiceSmall (Zero Cost, ~300x Speed)
│   └── NO  (Pure CPU / Low Spec)
│         ├── Has Cloud API Key configured? → Use Cloud Whisper API
│         └── No Cloud Key? → Run SenseVoiceSmall CPU mode with polite progress prompt
```
