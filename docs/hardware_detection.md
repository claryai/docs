# Hardware Detection and Optimization for Clary AI

This document outlines the hardware detection and optimization strategy for Clary AI, ensuring optimal performance across different hardware configurations for each tier.

## Overview

Clary AI needs to run efficiently on a variety of hardware configurations, from basic servers with minimal resources to high-performance machines with GPUs. This document describes how Clary AI detects available hardware resources and optimizes its performance accordingly.

## Hardware Detection

### System Resource Detection

Detect available system resources:

```python
import os
import psutil
import torch
import logging

logger = logging.getLogger(__name__)

class HardwareDetector:
    """Detect and report hardware capabilities."""
    
    def __init__(self):
        """Initialize the hardware detector."""
        self.cpu_count = psutil.cpu_count(logical=False)
        self.cpu_count_logical = psutil.cpu_count(logical=True)
        self.memory_total = psutil.virtual_memory().total
        self.memory_available = psutil.virtual_memory().available
        self.disk_total = psutil.disk_usage('/').total
        self.disk_free = psutil.disk_usage('/').free
        self.gpu_available = torch.cuda.is_available()
        self.gpu_count = torch.cuda.device_count() if self.gpu_available else 0
        self.gpu_names = [torch.cuda.get_device_name(i) for i in range(self.gpu_count)] if self.gpu_available else []
        self.gpu_memory = [torch.cuda.get_device_properties(i).total_memory for i in range(self.gpu_count)] if self.gpu_available else []
        
        logger.info(f"Detected hardware: {self.get_summary()}")
    
    def get_summary(self):
        """Get a summary of hardware capabilities."""
        return {
            "cpu": {
                "physical_cores": self.cpu_count,
                "logical_cores": self.cpu_count_logical
            },
            "memory": {
                "total_gb": round(self.memory_total / (1024**3), 2),
                "available_gb": round(self.memory_available / (1024**3), 2)
            },
            "disk": {
                "total_gb": round(self.disk_total / (1024**3), 2),
                "free_gb": round(self.disk_free / (1024**3), 2)
            },
            "gpu": {
                "available": self.gpu_available,
                "count": self.gpu_count,
                "devices": [
                    {
                        "name": name,
                        "memory_gb": round(memory / (1024**3), 2)
                    }
                    for name, memory in zip(self.gpu_names, self.gpu_memory)
                ] if self.gpu_available else []
            }
        }
    
    def meets_minimum_requirements(self, tier):
        """Check if the hardware meets minimum requirements for a tier."""
        requirements = {
            "lite": {
                "cpu_cores": 2,
                "memory_gb": 4,
                "disk_gb": 5,
                "gpu_required": False
            },
            "standard": {
                "cpu_cores": 4,
                "memory_gb": 8,
                "disk_gb": 10,
                "gpu_required": False
            },
            "professional": {
                "cpu_cores": 8,
                "memory_gb": 16,
                "disk_gb": 20,
                "gpu_required": False  # Recommended but not required
            }
        }
        
        if tier not in requirements:
            return False
        
        req = requirements[tier]
        
        # Check CPU
        if self.cpu_count < req["cpu_cores"]:
            logger.warning(f"CPU cores below minimum for {tier} tier: {self.cpu_count} < {req['cpu_cores']}")
            return False
        
        # Check memory
        memory_gb = self.memory_total / (1024**3)
        if memory_gb < req["memory_gb"]:
            logger.warning(f"Memory below minimum for {tier} tier: {memory_gb:.2f}GB < {req['memory_gb']}GB")
            return False
        
        # Check disk
        disk_gb = self.disk_total / (1024**3)
        if disk_gb < req["disk_gb"]:
            logger.warning(f"Disk space below minimum for {tier} tier: {disk_gb:.2f}GB < {req['disk_gb']}GB")
            return False
        
        # Check GPU if required
        if req["gpu_required"] and not self.gpu_available:
            logger.warning(f"GPU required for {tier} tier but not available")
            return False
        
        return True
    
    def get_optimal_configuration(self, tier):
        """Get optimal configuration based on available hardware."""
        config = {
            "threads": min(self.cpu_count_logical, 8),  # Default to 8 threads max
            "memory_limit_mb": int(self.memory_total * 0.7 / (1024**2)),  # Use up to 70% of memory
            "use_gpu": False,
            "gpu_layers": 0
        }
        
        # Adjust based on tier
        if tier == "lite":
            # Lite tier is CPU-only
            config["use_gpu"] = False
            config["gpu_layers"] = 0
        
        elif tier == "standard":
            # Standard tier can use GPU if available
            if self.gpu_available:
                config["use_gpu"] = True
                # Determine how many layers to offload based on GPU memory
                gpu_memory_gb = self.gpu_memory[0] / (1024**3)
                if gpu_memory_gb >= 8:
                    config["gpu_layers"] = -1  # All layers
                elif gpu_memory_gb >= 4:
                    config["gpu_layers"] = 32  # Partial offload
                else:
                    config["gpu_layers"] = 16  # Minimal offload
        
        elif tier == "professional":
            # Professional tier should use GPU if available
            if self.gpu_available:
                config["use_gpu"] = True
                # Determine how many layers to offload based on GPU memory
                gpu_memory_gb = self.gpu_memory[0] / (1024**3)
                if gpu_memory_gb >= 16:
                    config["gpu_layers"] = -1  # All layers
                elif gpu_memory_gb >= 8:
                    config["gpu_layers"] = 40  # Most layers
                elif gpu_memory_gb >= 4:
                    config["gpu_layers"] = 32  # Partial offload
                else:
                    config["gpu_layers"] = 16  # Minimal offload
        
        return config
```

### Model Optimization

Optimize model loading and inference based on available hardware:

```python
class ModelOptimizer:
    """Optimize model loading and inference based on hardware."""
    
    def __init__(self, hardware_detector):
        """Initialize the model optimizer."""
        self.hardware = hardware_detector
        self.config = {}
    
    def optimize_for_tier(self, tier):
        """Optimize configuration for a specific tier."""
        # Get optimal configuration based on hardware
        self.config = self.hardware.get_optimal_configuration(tier)
        
        # Set environment variables for optimization
        os.environ["OMP_NUM_THREADS"] = str(self.config["threads"])
        os.environ["MKL_NUM_THREADS"] = str(self.config["threads"])
        
        # Configure GPU usage
        if self.config["use_gpu"]:
            os.environ["LLM_GPU_LAYERS"] = str(self.config["gpu_layers"])
        else:
            os.environ["LLM_GPU_LAYERS"] = "0"
        
        logger.info(f"Optimized configuration for {tier} tier: {self.config}")
        
        return self.config
    
    def get_model_config(self, model_name):
        """Get optimized configuration for a specific model."""
        model_configs = {
            "phi-4-multimodal": {
                "context_length": min(4096, int(self.config["memory_limit_mb"] / 4)),
                "batch_size": min(512, int(self.config["memory_limit_mb"] / 32)),
                "gpu_layers": self.config["gpu_layers"] if self.config["use_gpu"] else 0
            },
            "llama-3-8b": {
                "context_length": min(4096, int(self.config["memory_limit_mb"] / 8)),
                "batch_size": min(512, int(self.config["memory_limit_mb"] / 64)),
                "gpu_layers": self.config["gpu_layers"] if self.config["use_gpu"] else 0
            }
        }
        
        if model_name not in model_configs:
            logger.warning(f"No optimization config for model: {model_name}")
            return {}
        
        return model_configs[model_name]
```

## Hardware Recommendations

Provide hardware recommendations based on detected hardware:

```python
class HardwareRecommender:
    """Provide hardware recommendations based on detected hardware."""
    
    def __init__(self, hardware_detector):
        """Initialize the hardware recommender."""
        self.hardware = hardware_detector
    
    def get_recommendations(self, tier):
        """Get hardware recommendations for a specific tier."""
        recommendations = []
        
        # CPU recommendations
        if tier == "lite" and self.hardware.cpu_count < 2:
            recommendations.append({
                "component": "CPU",
                "current": f"{self.hardware.cpu_count} cores",
                "recommended": "2+ cores",
                "impact": "Critical - Upgrade recommended for basic functionality"
            })
        elif tier == "standard" and self.hardware.cpu_count < 4:
            recommendations.append({
                "component": "CPU",
                "current": f"{self.hardware.cpu_count} cores",
                "recommended": "4+ cores",
                "impact": "High - Performance will be degraded"
            })
        elif tier == "professional" and self.hardware.cpu_count < 8:
            recommendations.append({
                "component": "CPU",
                "current": f"{self.hardware.cpu_count} cores",
                "recommended": "8+ cores",
                "impact": "Medium - Performance may be degraded for complex documents"
            })
        
        # Memory recommendations
        memory_gb = self.hardware.memory_total / (1024**3)
        if tier == "lite" and memory_gb < 4:
            recommendations.append({
                "component": "Memory",
                "current": f"{memory_gb:.2f}GB",
                "recommended": "4GB+",
                "impact": "Critical - Upgrade recommended for basic functionality"
            })
        elif tier == "standard" and memory_gb < 8:
            recommendations.append({
                "component": "Memory",
                "current": f"{memory_gb:.2f}GB",
                "recommended": "8GB+",
                "impact": "High - Performance will be degraded"
            })
        elif tier == "professional" and memory_gb < 16:
            recommendations.append({
                "component": "Memory",
                "current": f"{memory_gb:.2f}GB",
                "recommended": "16GB+",
                "impact": "Medium - Performance may be degraded for complex documents"
            })
        
        # Disk recommendations
        disk_gb = self.hardware.disk_free / (1024**3)
        if tier == "lite" and disk_gb < 5:
            recommendations.append({
                "component": "Disk",
                "current": f"{disk_gb:.2f}GB free",
                "recommended": "5GB+ free",
                "impact": "Medium - Limited space for document storage"
            })
        elif tier == "standard" and disk_gb < 10:
            recommendations.append({
                "component": "Disk",
                "current": f"{disk_gb:.2f}GB free",
                "recommended": "10GB+ free",
                "impact": "Medium - Limited space for models and document storage"
            })
        elif tier == "professional" and disk_gb < 20:
            recommendations.append({
                "component": "Disk",
                "current": f"{disk_gb:.2f}GB free",
                "recommended": "20GB+ free",
                "impact": "Medium - Limited space for models and document storage"
            })
        
        # GPU recommendations
        if tier == "standard" and not self.hardware.gpu_available:
            recommendations.append({
                "component": "GPU",
                "current": "Not available",
                "recommended": "Optional - Any CUDA-compatible GPU",
                "impact": "Low - Performance improvement with GPU"
            })
        elif tier == "professional" and not self.hardware.gpu_available:
            recommendations.append({
                "component": "GPU",
                "current": "Not available",
                "recommended": "Recommended - CUDA-compatible GPU with 8GB+ VRAM",
                "impact": "Medium - Significant performance improvement with GPU"
            })
        elif tier == "professional" and self.hardware.gpu_available:
            gpu_memory_gb = self.hardware.gpu_memory[0] / (1024**3)
            if gpu_memory_gb < 8:
                recommendations.append({
                    "component": "GPU",
                    "current": f"{self.hardware.gpu_names[0]} with {gpu_memory_gb:.2f}GB VRAM",
                    "recommended": "CUDA-compatible GPU with 8GB+ VRAM",
                    "impact": "Low - Performance improvement with more VRAM"
                })
        
        return recommendations
```

## Implementation in API

Expose hardware detection and recommendations through API endpoints:

```python
@app.get("/api/v1/system/hardware", response_model=HardwareInfo)
async def get_hardware_info(
    current_user: User = Depends(get_api_key)
):
    """
    Get hardware information.
    
    Returns:
        HardwareInfo: Hardware information.
    """
    # Get hardware detector
    hardware_detector = HardwareDetector()
    
    # Get hardware summary
    hardware_info = hardware_detector.get_summary()
    
    # Get tier
    tier = current_user.tier if current_user else "lite"
    
    # Check if hardware meets minimum requirements
    hardware_info["meets_requirements"] = hardware_detector.meets_minimum_requirements(tier)
    
    # Get optimal configuration
    model_optimizer = ModelOptimizer(hardware_detector)
    hardware_info["optimal_config"] = model_optimizer.optimize_for_tier(tier)
    
    # Get recommendations
    recommender = HardwareRecommender(hardware_detector)
    hardware_info["recommendations"] = recommender.get_recommendations(tier)
    
    return hardware_info
```

## Adaptive Configuration

Implement adaptive configuration based on hardware detection:

```python
def configure_system_for_hardware():
    """Configure the system based on detected hardware."""
    # Detect hardware
    hardware_detector = HardwareDetector()
    
    # Get tier from environment
    tier = os.environ.get("TIER", "lite")
    
    # Check if hardware meets minimum requirements
    if not hardware_detector.meets_minimum_requirements(tier):
        logger.warning(f"Hardware does not meet minimum requirements for {tier} tier")
        # Fall back to lite tier if hardware doesn't meet requirements
        if tier != "lite":
            logger.warning(f"Falling back to lite tier due to hardware limitations")
            os.environ["TIER"] = "lite"
            tier = "lite"
    
    # Optimize for tier
    model_optimizer = ModelOptimizer(hardware_detector)
    config = model_optimizer.optimize_for_tier(tier)
    
    # Apply configuration
    logger.info(f"Applying hardware-optimized configuration: {config}")
    
    # Return configuration
    return config
```

## User Interface Integration

Integrate hardware detection and recommendations into the user interface:

1. **System Information Page**:
   - Display detected hardware
   - Show hardware recommendations
   - Provide upgrade guidance

2. **Performance Optimization**:
   - Allow users to adjust configuration
   - Provide performance impact estimates
   - Save custom configurations

3. **Tier Selection Guidance**:
   - Recommend appropriate tier based on hardware
   - Show performance expectations
   - Highlight hardware limitations
