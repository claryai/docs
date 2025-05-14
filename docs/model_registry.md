# Model Registry for Clary AI

This document outlines the design and implementation of the model registry for Clary AI, which provides tier-based access to AI models and manages model versioning, downloading, and updates.

## Overview

The model registry is a core component of Clary AI that manages AI models across different tiers. It ensures that:

1. Each tier has access to the appropriate models
2. Models are downloaded and updated efficiently
3. Model versions are tracked and managed
4. Users can easily discover available models

## Architecture

### Components

The model registry consists of the following components:

1. **Model Catalog**: Maintains a catalog of available models and their metadata
2. **Model Storage**: Manages the storage of model files
3. **Model Downloader**: Handles downloading models from external sources
4. **Model Versioning**: Tracks model versions and updates
5. **Access Control**: Enforces tier-based access to models
6. **API**: Provides APIs for model discovery, download, and management
7. **UI**: Provides a user interface for model management

### Data Model

```python
class ModelMetadata(BaseModel):
    """Model metadata."""
    
    id: str
    name: str
    description: str
    type: str  # llm, layout, ocr, etc.
    version: str
    size_bytes: int
    filename: str
    repo_id: str
    download_url: str
    tier: str  # lite, standard, professional
    created_at: datetime
    updated_at: datetime
    parameters: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    
    class Config:
        """Pydantic config."""
        
        orm_mode = True


class ModelVersion(BaseModel):
    """Model version."""
    
    model_id: str
    version: str
    filename: str
    size_bytes: int
    download_url: str
    created_at: datetime
    changes: Optional[str] = None
    
    class Config:
        """Pydantic config."""
        
        orm_mode = True


class ModelDownload(BaseModel):
    """Model download record."""
    
    model_id: str
    version: str
    downloaded_at: datetime
    status: str  # success, failed
    error: Optional[str] = None
    
    class Config:
        """Pydantic config."""
        
        orm_mode = True
```

## Implementation

### Model Catalog

The model catalog maintains a list of available models and their metadata:

```python
class ModelCatalog:
    """Model catalog."""
    
    def __init__(self, db_session):
        """Initialize the model catalog."""
        self.db = db_session
    
    def get_models(self, tier: str = None, model_type: str = None) -> List[ModelMetadata]:
        """
        Get models.
        
        Args:
            tier: Filter by tier.
            model_type: Filter by model type.
            
        Returns:
            List[ModelMetadata]: List of models.
        """
        query = self.db.query(ModelMetadata)
        
        if tier:
            # For professional tier, return all models
            if tier == "professional":
                pass
            # For standard tier, return standard and lite models
            elif tier == "standard":
                query = query.filter(ModelMetadata.tier.in_(["standard", "lite"]))
            # For lite tier, return only lite models
            elif tier == "lite":
                query = query.filter(ModelMetadata.tier == "lite")
        
        if model_type:
            query = query.filter(ModelMetadata.type == model_type)
        
        return query.all()
    
    def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        """
        Get a model by ID.
        
        Args:
            model_id: Model ID.
            
        Returns:
            Optional[ModelMetadata]: Model metadata.
        """
        return self.db.query(ModelMetadata).filter(ModelMetadata.id == model_id).first()
    
    def add_model(self, model: ModelMetadata) -> ModelMetadata:
        """
        Add a model.
        
        Args:
            model: Model metadata.
            
        Returns:
            ModelMetadata: Added model metadata.
        """
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model
    
    def update_model(self, model_id: str, model: ModelMetadata) -> Optional[ModelMetadata]:
        """
        Update a model.
        
        Args:
            model_id: Model ID.
            model: Model metadata.
            
        Returns:
            Optional[ModelMetadata]: Updated model metadata.
        """
        db_model = self.db.query(ModelMetadata).filter(ModelMetadata.id == model_id).first()
        
        if not db_model:
            return None
        
        for key, value in model.dict(exclude_unset=True).items():
            setattr(db_model, key, value)
        
        self.db.commit()
        self.db.refresh(db_model)
        return db_model
    
    def delete_model(self, model_id: str) -> bool:
        """
        Delete a model.
        
        Args:
            model_id: Model ID.
            
        Returns:
            bool: True if deleted, False otherwise.
        """
        db_model = self.db.query(ModelMetadata).filter(ModelMetadata.id == model_id).first()
        
        if not db_model:
            return False
        
        self.db.delete(db_model)
        self.db.commit()
        return True
```

### Model Downloader

The model downloader handles downloading models from external sources:

```python
class ModelDownloader:
    """Model downloader."""
    
    def __init__(self, model_dir: str, db_session):
        """Initialize the model downloader."""
        self.model_dir = model_dir
        self.db = db_session
    
    async def download_model(self, model_id: str, force: bool = False) -> bool:
        """
        Download a model.
        
        Args:
            model_id: Model ID.
            force: Force download even if model exists.
            
        Returns:
            bool: True if downloaded, False otherwise.
        """
        # Get model metadata
        model = self.db.query(ModelMetadata).filter(ModelMetadata.id == model_id).first()
        
        if not model:
            logger.error(f"Model not found: {model_id}")
            return False
        
        # Create model directory
        model_path = os.path.join(self.model_dir, model.type, model.filename)
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Check if model already exists
        if os.path.exists(model_path) and not force:
            logger.info(f"Model already exists: {model_id}")
            return True
        
        # Download model
        try:
            logger.info(f"Downloading model: {model_id}")
            
            # Create a download record
            download = ModelDownload(
                model_id=model_id,
                version=model.version,
                downloaded_at=datetime.now(),
                status="in_progress"
            )
            self.db.add(download)
            self.db.commit()
            
            # Download model
            if model.repo_id:
                # Download from Hugging Face
                huggingface_hub.hf_hub_download(
                    repo_id=model.repo_id,
                    filename=model.filename,
                    local_dir=os.path.dirname(model_path),
                    local_dir_use_symlinks=False,
                )
            else:
                # Download from URL
                async with aiohttp.ClientSession() as session:
                    async with session.get(model.download_url) as response:
                        if response.status != 200:
                            raise Exception(f"Failed to download model: {response.status}")
                        
                        with open(model_path, "wb") as f:
                            while True:
                                chunk = await response.content.read(1024 * 1024)
                                if not chunk:
                                    break
                                f.write(chunk)
            
            # Update download record
            download.status = "success"
            self.db.commit()
            
            logger.info(f"Model downloaded successfully: {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading model {model_id}: {e}")
            
            # Update download record
            download.status = "failed"
            download.error = str(e)
            self.db.commit()
            
            return False
```

### Access Control

The access control component enforces tier-based access to models:

```python
class ModelAccessControl:
    """Model access control."""
    
    def __init__(self, db_session):
        """Initialize the model access control."""
        self.db = db_session
    
    def can_access_model(self, model_id: str, tier: str) -> bool:
        """
        Check if a tier can access a model.
        
        Args:
            model_id: Model ID.
            tier: Tier.
            
        Returns:
            bool: True if the tier can access the model, False otherwise.
        """
        # Get model metadata
        model = self.db.query(ModelMetadata).filter(ModelMetadata.id == model_id).first()
        
        if not model:
            return False
        
        # For professional tier, all models are accessible
        if tier == "professional":
            return True
        
        # For standard tier, standard and lite models are accessible
        if tier == "standard":
            return model.tier in ["standard", "lite"]
        
        # For lite tier, only lite models are accessible
        if tier == "lite":
            return model.tier == "lite"
        
        return False
```

## API Endpoints

The model registry provides the following API endpoints:

```python
@app.get("/api/v1/models", response_model=List[ModelMetadata])
async def get_models(
    tier: Optional[str] = None,
    model_type: Optional[str] = None,
    current_user: User = Depends(get_api_key),
    db: Session = Depends(get_db),
):
    """
    Get models.
    
    Args:
        tier: Filter by tier.
        model_type: Filter by model type.
        current_user: Current user.
        db: Database session.
        
    Returns:
        List[ModelMetadata]: List of models.
    """
    # Get user's tier if not specified
    if not tier:
        tier = current_user.tier
    
    # Get models
    catalog = ModelCatalog(db)
    return catalog.get_models(tier=tier, model_type=model_type)


@app.get("/api/v1/models/{model_id}", response_model=ModelMetadata)
async def get_model(
    model_id: str,
    current_user: User = Depends(get_api_key),
    db: Session = Depends(get_db),
):
    """
    Get a model.
    
    Args:
        model_id: Model ID.
        current_user: Current user.
        db: Database session.
        
    Returns:
        ModelMetadata: Model metadata.
    """
    # Get model
    catalog = ModelCatalog(db)
    model = catalog.get_model(model_id)
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Check access
    access_control = ModelAccessControl(db)
    if not access_control.can_access_model(model_id, current_user.tier):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return model


@app.post("/api/v1/models/{model_id}/download")
async def download_model(
    model_id: str,
    force: bool = False,
    current_user: User = Depends(get_api_key),
    db: Session = Depends(get_db),
):
    """
    Download a model.
    
    Args:
        model_id: Model ID.
        force: Force download even if model exists.
        current_user: Current user.
        db: Database session.
        
    Returns:
        dict: Download status.
    """
    # Check access
    access_control = ModelAccessControl(db)
    if not access_control.can_access_model(model_id, current_user.tier):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Download model
    downloader = ModelDownloader(settings.MODEL_PATH, db)
    success = await downloader.download_model(model_id, force)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to download model")
    
    return {"status": "success"}
```

## User Interface

The model registry provides a user interface for model management:

1. **Model Discovery**:
   - List available models for the user's tier
   - Filter models by type, size, etc.
   - View model details and metadata

2. **Model Management**:
   - Download and update models
   - View download status and progress
   - Manage model storage

3. **Model Usage**:
   - Select models for document processing
   - Configure model parameters
   - View model performance metrics

## Initialization

Initialize the model registry with default models:

```python
def initialize_model_registry(db: Session):
    """
    Initialize the model registry with default models.
    
    Args:
        db: Database session.
    """
    # Create model catalog
    catalog = ModelCatalog(db)
    
    # Define default models
    default_models = [
        ModelMetadata(
            id="llama-3-8b",
            name="Llama 3 8B",
            description="Llama 3 8B model for professional tier",
            type="llm",
            version="1.0.0",
            size_bytes=4_000_000_000,  # 4GB
            filename="llama-3-8b.Q4_K_M.gguf",
            repo_id="TheBloke/Llama-3-8B-GGUF",
            download_url="https://huggingface.co/TheBloke/Llama-3-8B-GGUF/resolve/main/llama-3-8b.Q4_K_M.gguf",
            tier="professional",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            parameters={
                "context_length": 4096,
                "batch_size": 512,
            },
            tags=["llm", "professional", "llama"],
        ),
        ModelMetadata(
            id="phi-4-multimodal",
            name="Phi-4 Multimodal",
            description="Phi-4 Multimodal model for standard tier",
            type="llm",
            version="1.0.0",
            size_bytes=2_000_000_000,  # 2GB
            filename="phi-4-multimodal.Q4_K_M.gguf",
            repo_id="microsoft/Phi-4-Multimodal-GGUF",
            download_url="https://huggingface.co/microsoft/Phi-4-Multimodal-GGUF/resolve/main/phi-4-multimodal.Q4_K_M.gguf",
            tier="standard",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            parameters={
                "context_length": 4096,
                "batch_size": 512,
            },
            tags=["llm", "standard", "phi", "multimodal"],
        ),
        ModelMetadata(
            id="layoutlmv3",
            name="LayoutLMv3",
            description="LayoutLMv3 model for document layout analysis",
            type="layout",
            version="1.0.0",
            size_bytes=500_000_000,  # 500MB
            filename="layoutlmv3-base",
            repo_id="microsoft/layoutlmv3-base",
            download_url="https://huggingface.co/microsoft/layoutlmv3-base",
            tier="lite",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            parameters={},
            tags=["layout", "lite", "layoutlm"],
        ),
    ]
    
    # Add default models
    for model in default_models:
        existing_model = catalog.get_model(model.id)
        if not existing_model:
            catalog.add_model(model)
```
