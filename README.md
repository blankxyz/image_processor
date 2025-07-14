
  A comprehensive guide for handling File type parameters in Dify plugin development, based on real-world experience building an image resizing plugin.

  🎯 Overview

  This repository contains the complete documentation and example code for properly handling File type parameters in Dify plugins. It addresses common issues developers face when working with file inputs and outputs in the Dify
  plugin ecosystem.

  当前的main版本为输入url的内容，如果需要文件版本，请参考0.0.1

  📚 What's Included

  - Complete Documentation: Detailed guide covering all aspects of File parameter handling
  - Working Code Examples: Real implementation of an image resizing plugin
  - Best Practices: Proven patterns from successful plugin development
  - Troubleshooting Guide: Solutions to common problems and error messages

  🚀 Quick Start

  Problem Statement

  When developing Dify plugins that handle files, developers often encounter:

  NameError: name 'File' is not defined
  ToolIdentity() argument after ** must be a mapping, not NoneType
  "file对象不能作为输出参数使用" (File objects cannot be used as output parameters)
  "file对象不能作为输入参数使用" (File objects cannot be used as input parameters)

  Solution Overview

  ✅ Correct Parameter Configuration
  parameters:
    - name: input_image
      type: files  # Use 'files' not 'file'
      required: true

  ✅ Proper Imports
  from dify_plugin.file.file import File  # Critical import path
  from dify_plugin import Tool
  from dify_plugin.entities.tool import ToolInvokeMessage

  ✅ File Output Method
  meta = {
      "filename": "processed_image.jpg",
      "mime_type": "image/jpeg",
      "size": file_size,
  }
  yield self.create_blob_message(file_data, meta)

  📖 Documentation

  Main Guide

  - ./dify-file-parameter-guide.md - The comprehensive documentation

  Key Sections

  1. File Type Limitations - Understanding what works and what doesn't
  2. Correct Import Methods - Essential import statements and paths
  3. File Processing Best Practices - Proven patterns for file handling
  4. Parameter Configuration - YAML setup and validation
  5. Error Handling - Comprehensive error management strategies
  6. Complete Examples - Working code implementations

  🛠️ Example Plugin

  This repository includes a complete working example: Image Resize to 1080p Plugin

  Features

  - Resize images to 1080p resolution
  - Multiple resize methods (fit, crop, stretch)
  - Support for JPEG, PNG, WebP formats
  - Quality control for output
  - Comprehensive error handling

  File Structure

  image-resizer-plugin/
  ├── manifest.yaml
  ├── provider/
  │   └── image_resizer.yaml
  ├── tools/
  │   ├── resize_to_1080p.yaml
  │   └── resize_to_1080p.py
  ├── image_resizer.py
  ├── _assets/
  │   └── icon.svg
  └── requirements.txt

  🔧 Key Insights

  What We Learned

  1. Use files not file - The parameter type must be plural
  2. Correct import path - from dify_plugin.file.file import File
  3. File output method - Use create_blob_message() for file outputs
  4. Reference working plugins - Study existing successful implementations
  5. Host URL handling - Proper URL construction for file access

  Common Pitfalls

  ❌ Wrong parameter type
  type: file  # This doesn't work

  ❌ Incorrect import
  from dify_plugin import File  # Wrong path

  ❌ Direct file return
  return processed_file  # Files can't be returned directly

  🎯 Target Audience

  - Dify plugin developers working with file inputs/outputs
  - Developers encountering file parameter errors
  - Teams building image, document, or media processing plugins
  - Anyone wanting to understand Dify's file handling architecture

  🤝 Contributing

  Found an issue or have improvements? We welcome contributions!

  1. Fork the repository
  2. Create your feature branch
  3. Submit a pull request with detailed description

  📝 Development Experience

  This guide is based on the actual development of an image processing plugin, including:

  - Initial failures and error messages
  - Discovery of working patterns through existing code analysis
  - Step-by-step problem solving
  - Final working implementation

  🔗 Related Resources

  - https://docs.dify.ai/plugins
  - https://github.com/langgenius/dify-plugin-sdks
  - https://github.com/langgenius/dify

  📄 License

  This project is licensed under the MIT License - see the LICENSE file for details.

  ⭐ Star This Repository

  If this guide helped you solve file parameter issues in your Dify plugin development, please give it a star! ⭐
