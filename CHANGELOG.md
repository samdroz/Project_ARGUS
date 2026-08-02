# Changelog

All notable changes to **Project ARGUS** will be documented in this file.

The format is inspired by [Keep a Changelog](https://keepachangelog.com/), and the project follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

_No unreleased changes yet._

---

## [1.1.0] - 2026-08-02

### 🚀 Added

#### AI Modules
- Image deepfake detection using Vision Transformers
- Video deepfake detection using frame-by-frame analysis
- Text fake news detection using a RoBERTa classifier
- Metadata analysis utilities
- Explainable Trust Engine
- Model Manager for centralized AI model loading

#### Backend
- FastAPI REST API
- Standardized response schema
- Health check endpoint
- Upload validation
- GPU (CUDA) support
- Environment-based configuration
- Centralized logging
- Modular service layer

#### Project Structure
- Dedicated AI modules
- Service layer architecture
- Config management
- Utility modules
- Test suite
- API schemas

### ✨ Improved
- Refined trust score calculation logic
- Strengthened the recommendation engine
- Tuned risk assessment logic
- Expanded explainable AI factors
- Improved API response consistency
- Updated project documentation
- Reorganized repository structure
- Optimized model loading performance
- Improved error reporting
- Improved health monitoring

### 🛠 Fixed
- Fixed duplicate imports
- Fixed model loading issues
- Fixed video frame extraction bugs
- Resolved OpenCV compatibility issues
- Cleaned up test organization
- Cleaned up repository structure
- Fixed upload validation issues
- Fixed configuration inconsistencies

### 📚 Documentation
- Rewrote README for a professional presentation
- Added an installation guide
- Added a project architecture overview
- Added an API reference
- Documented environment configuration
- Added usage examples

### 🔒 Security
- Added file type validation on uploads
- Enforced upload size limits
- Improved exception handling
- Made API responses safer

### ⚡ Performance
- Added CUDA-accelerated inference
- Centralized model loading through the Model Manager
- Reduced duplicate model initialization
- Optimized the service-layer architecture

---

## [1.0.0] - Initial Release

Initial implementation of the Project ARGUS backend.

### 🚀 Added
- Basic FastAPI backend
- Initial image detection
- Initial project structure