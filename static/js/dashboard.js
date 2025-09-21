// Dashboard JavaScript Functionality
class ResumeDashboard {
  constructor() {
    this.jobFile = null;
    this.resumeFiles = [];
    this.analysisResults = [];
    this.charts = {};
    this.filters = {
      minScore: 0,
      requiredSkills: [],
      candidateName: "",
    };

    // Pagination settings
    this.pagination = {
      currentPage: 1,
      itemsPerPage: 10,
      totalPages: 1,
    };

    // Enhanced dual upload functionality
    this.dualUpload = {
      mode: "standard", // 'standard' or 'dual' or 'batch'
      jobDescriptions: [],
      resumes: [],
      analysisMatrix: [],
      currentAnalysis: null,
    };

    // Add debug logging
    this.debug = true;
    this.log = (message, data = null) => {
      if (this.debug) {
        console.log(`[ResumeDashboard] ${message}`, data || "");
      }
    };

    this.init();
  }

  init() {
    this.log("Initializing dashboard...");
    try {
      this.setupEventListeners();
      this.setupDualUploadFeatures();
      this.checkSystemHealth();
      this.initializeCharts();
      this.log("Dashboard initialized successfully");
    } catch (error) {
      console.error("Dashboard initialization failed:", error);
      this.showError("Failed to initialize dashboard: " + error.message);
    }
  }

  setupDualUploadFeatures() {
    this.log("Setting up dual upload features...");

    // Add enhanced upload mode toggle
    const uploadModeToggle = document.createElement("div");
    uploadModeToggle.className = "upload-mode-toggle mb-3";
    uploadModeToggle.innerHTML = `
      <div class="btn-group w-100" role="group" aria-label="Upload Mode">
        <input type="radio" class="btn-check" name="uploadMode" id="mode-standard" value="standard" checked>
        <label class="btn btn-outline-primary" for="mode-standard">
          <i class="fas fa-file-alt me-1"></i>Standard Upload
        </label>
        
        <input type="radio" class="btn-check" name="uploadMode" id="mode-dual" value="dual">
        <label class="btn btn-outline-primary" for="mode-dual">
          <i class="fas fa-files me-1"></i>Dual Upload
        </label>
        
        <input type="radio" class="btn-check" name="uploadMode" id="mode-batch" value="batch">
        <label class="btn btn-outline-primary" for="mode-batch">
          <i class="fas fa-layer-group me-1"></i>Batch Process
        </label>
      </div>
    `;

    // Insert before the first upload area
    const firstUploadArea = document.querySelector(".upload-area").parentNode;
    firstUploadArea.parentNode.insertBefore(uploadModeToggle, firstUploadArea);

    // Add event listeners for upload mode
    document.querySelectorAll('input[name="uploadMode"]').forEach((radio) => {
      radio.addEventListener("change", (e) =>
        this.changeUploadMode(e.target.value)
      );
    });

    // Add dual upload status panel
    this.createDualUploadStatusPanel();

    // Add batch processing controls
    this.createBatchProcessingControls();
  }

  changeUploadMode(mode) {
    this.log(`Changing upload mode to: ${mode}`);
    this.dualUpload.mode = mode;

    // Update UI based on mode
    const standardElements = document.querySelectorAll(".standard-mode");
    const dualElements = document.querySelectorAll(".dual-mode");
    const batchElements = document.querySelectorAll(".batch-mode");

    // Hide all mode-specific elements
    [...standardElements, ...dualElements, ...batchElements].forEach((el) => {
      el.style.display = "none";
    });

    // Show elements for current mode
    const currentModeElements = document.querySelectorAll(`.${mode}-mode`);
    currentModeElements.forEach((el) => {
      el.style.display = "block";
    });

    // Update analyze button text
    const analyzeBtn = document.getElementById("analyze-btn");
    switch (mode) {
      case "dual":
        analyzeBtn.innerHTML =
          '<i class="fas fa-magic me-1"></i>Analyze All Combinations';
        break;
      case "batch":
        analyzeBtn.innerHTML =
          '<i class="fas fa-rocket me-1"></i>Batch Process & Analyze';
        break;
      default:
        analyzeBtn.innerHTML =
          '<i class="fas fa-search me-1"></i>Analyze Resumes';
    }

    // Update upload areas for multiple files if needed
    if (mode === "dual" || mode === "batch") {
      this.enableMultipleFileUploads();
    } else {
      this.resetToStandardUpload();
    }
  }

  createDualUploadStatusPanel() {
    const statusPanel = document.createElement("div");
    statusPanel.className = "dual-upload-status dual-mode batch-mode";
    statusPanel.style.display = "none";
    statusPanel.innerHTML = `
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-gradient-primary text-white">
          <h6 class="mb-0">
            <i class="fas fa-list-check me-2"></i>Upload Status
          </h6>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <div class="status-group">
                <h6 class="text-muted">Job Descriptions (<span id="job-count">0</span>)</h6>
                <div id="job-descriptions-list" class="file-list mb-3"></div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="status-group">
                <h6 class="text-muted">Resumes (<span id="resume-count">0</span>)</h6>
                <div id="resumes-list" class="file-list mb-3"></div>
              </div>
            </div>
          </div>
          <div class="analysis-matrix mt-3" id="analysis-matrix" style="display: none;">
            <h6 class="text-muted">Analysis Matrix</h6>
            <div id="matrix-content" class="matrix-grid"></div>
          </div>
        </div>
      </div>
    `;

    // Insert after upload areas
    const uploadSection = document.querySelector(".row:has(.upload-area)");
    uploadSection.parentNode.insertBefore(
      statusPanel,
      uploadSection.nextSibling
    );
  }

  createBatchProcessingControls() {
    const controlsPanel = document.createElement("div");
    controlsPanel.className = "batch-processing-controls batch-mode";
    controlsPanel.style.display = "none";
    controlsPanel.innerHTML = `
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-gradient-secondary text-white">
          <h6 class="mb-0">
            <i class="fas fa-cogs me-2"></i>Analysis Options
          </h6>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <div class="form-check form-switch mb-2">
                <input class="form-check-input" type="checkbox" id="include-skills" checked>
                <label class="form-check-label" for="include-skills">Skill Analysis</label>
              </div>
              <div class="form-check form-switch mb-2">
                <input class="form-check-input" type="checkbox" id="include-experience" checked>
                <label class="form-check-label" for="include-experience">Experience Analysis</label>
              </div>
              <div class="form-check form-switch mb-2">
                <input class="form-check-input" type="checkbox" id="include-semantic" checked>
                <label class="form-check-label" for="include-semantic">Semantic Similarity</label>
              </div>
            </div>
            <div class="col-md-6">
              <div class="form-check form-switch mb-2">
                <input class="form-check-input" type="checkbox" id="include-feedback" checked>
                <label class="form-check-label" for="include-feedback">Generate Feedback</label>
              </div>
              <div class="form-check form-switch mb-2">
                <input class="form-check-input" type="checkbox" id="include-comparison" checked>
                <label class="form-check-label" for="include-comparison">Comparative Analysis</label>
              </div>
              <div class="form-check form-switch mb-2">
                <input class="form-check-input" type="checkbox" id="cross-analysis" checked>
                <label class="form-check-label" for="cross-analysis">Cross Analysis (All x All)</label>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    const statusPanel = document.querySelector(".dual-upload-status");
    statusPanel.parentNode.insertBefore(controlsPanel, statusPanel.nextSibling);
  }

  enableMultipleFileUploads() {
    // Update job description input to accept multiple files
    const jobInput = document.getElementById("job-file");
    jobInput.setAttribute("multiple", "true");

    // Update resume input (already supports multiple)
    const resumeInput = document.getElementById("resume-file");
    resumeInput.setAttribute("multiple", "true");

    // Update upload area text
    const jobArea = document.getElementById("job-upload-area");
    const resumeArea = document.getElementById("resume-upload-area");

    const originalJobText = jobArea.querySelector(".upload-text");
    const originalResumeText = resumeArea.querySelector(".upload-text");

    if (originalJobText) {
      originalJobText.innerHTML = `
        <i class="fas fa-cloud-upload-alt fa-3x mb-3"></i>
        <h5>Upload Multiple Job Descriptions</h5>
        <p>Drag & drop multiple job description files here or click to browse</p>
        <small>Supports PDF, DOC, DOCX, TXT</small>
      `;
    }

    if (originalResumeText) {
      originalResumeText.innerHTML = `
        <i class="fas fa-cloud-upload-alt fa-3x mb-3"></i>
        <h5>Upload Multiple Resumes</h5>
        <p>Drag & drop multiple resume files here or click to browse</p>
        <small>Supports PDF, DOC, DOCX, TXT</small>
      `;
    }
  }

  resetToStandardUpload() {
    // Remove multiple attribute
    const jobInput = document.getElementById("job-file");
    const resumeInput = document.getElementById("resume-file");

    jobInput.removeAttribute("multiple");
    // Keep multiple for resumes as it was originally designed for multiple resumes

    // Reset upload area text
    const jobArea = document.getElementById("job-upload-area");
    const originalJobText = jobArea.querySelector(".upload-text");

    if (originalJobText) {
      originalJobText.innerHTML = `
        <i class="fas fa-cloud-upload-alt fa-3x mb-3"></i>
        <h5>Upload Job Description</h5>
        <p>Drag & drop job description file here or click to browse</p>
        <small>Supports PDF, DOC, DOCX, TXT</small>
      `;
    }
  }

  setupEventListeners() {
    // File upload listeners
    this.setupFileUpload("job-file", "job-upload-area", false);
    this.setupFileUpload("resume-file", "resume-upload-area", true);

    // Button listeners
    document
      .getElementById("analyze-btn")
      .addEventListener("click", () => this.analyzeResumes());
    document
      .getElementById("clear-results")
      .addEventListener("click", () => this.clearResults());
    document
      .getElementById("export-results")
      .addEventListener("click", () => this.exportResults());

    // Filter listeners
    document
      .getElementById("apply-filters")
      .addEventListener("click", () => this.applyFilters());
    document
      .getElementById("reset-filters")
      .addEventListener("click", () => this.resetFilters());
    document
      .getElementById("min-score-filter")
      .addEventListener("input", (e) => {
        document.getElementById("min-score-value").textContent =
          e.target.value + "%";
      });

    // Sort listener
    document
      .getElementById("sort-candidates")
      .addEventListener("change", () => this.sortCandidates());
  }

  setupFileUpload(inputId, areaId, multiple = false) {
    const input = document.getElementById(inputId);
    const area = document.getElementById(areaId);

    // Drag and drop
    area.addEventListener("dragover", (e) => {
      e.preventDefault();
      area.classList.add("dragover");
    });

    area.addEventListener("dragleave", () => {
      area.classList.remove("dragover");
    });

    area.addEventListener("drop", (e) => {
      e.preventDefault();
      area.classList.remove("dragover");
      const files = Array.from(e.dataTransfer.files);
      this.handleFileSelection(files, inputId, multiple);
    });

    // Click to upload
    area.addEventListener("click", () => input.click());

    // File input change
    input.addEventListener("change", (e) => {
      const files = Array.from(e.target.files);
      this.handleFileSelection(files, inputId, multiple);
    });
  }

  async handleFileSelection(files, inputType, multiple) {
    const isJob = inputType.includes("job");

    // Handle dual upload mode differently
    if (this.dualUpload.mode === "dual" || this.dualUpload.mode === "batch") {
      return await this.handleDualFileSelection(files, isJob);
    }

    // Standard mode handling
    const progressId = isJob ? "job-progress" : "resume-progress";
    const statusId = isJob ? "job-status" : "resume-status";
    const areaId = isJob ? "job-upload-area" : "resume-upload-area";

    if (!multiple && files.length > 1) {
      files = [files[0]];
    }

    // Show progress
    document.getElementById(progressId).style.display = "block";
    const progressBar = document
      .getElementById(progressId)
      .querySelector(".progress-bar");

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];

        // Update progress
        const progress = ((i + 1) / files.length) * 100;
        progressBar.style.width = `${progress}%`;

        // Upload file
        const result = await this.uploadFile(file, isJob);

        if (result.success !== false) {
          if (isJob) {
            this.jobFile = result;
          } else {
            this.resumeFiles.push(result);
          }
        }
      }

      // Update UI
      document.getElementById(areaId).classList.add("success");
      document.getElementById(statusId).innerHTML = `
                <i class="fas fa-check-circle text-success me-1"></i>
                <span class="status-success">${files.length} file(s) uploaded successfully</span>
            `;

      this.updateAnalyzeButton();
    } catch (error) {
      document.getElementById(areaId).classList.add("error");
      document.getElementById(statusId).innerHTML = `
                <i class="fas fa-exclamation-circle text-danger me-1"></i>
                <span class="status-error">Upload failed: ${error.message}</span>
            `;
    }

    // Hide progress after delay
    setTimeout(() => {
      document.getElementById(progressId).style.display = "none";
      progressBar.style.width = "0%";
    }, 2000);
  }

  async handleDualFileSelection(files, isJob) {
    this.log(
      `Handling dual file selection: ${files.length} ${
        isJob ? "job" : "resume"
      } files`
    );

    try {
      // For dual mode, accumulate files and upload them together
      if (isJob) {
        // Add to job files list (we'll upload later)
        this.dualUpload.pendingJobFiles = (
          this.dualUpload.pendingJobFiles || []
        ).concat(Array.from(files));
      } else {
        // Add to resume files list (we'll upload later)
        this.dualUpload.pendingResumeFiles = (
          this.dualUpload.pendingResumeFiles || []
        ).concat(Array.from(files));
      }

      // Update status
      const statusId = isJob ? "job-status" : "resume-status";
      const areaId = isJob ? "job-upload-area" : "resume-upload-area";

      document.getElementById(areaId).classList.add("success");
      document.getElementById(statusId).innerHTML = `
        <i class="fas fa-check-circle text-success me-1"></i>
        <span class="status-success">${files.length} file(s) ready for upload</span>
      `;

      // Check if we have both types and can perform dual upload
      if (
        this.dualUpload.pendingJobFiles?.length > 0 &&
        this.dualUpload.pendingResumeFiles?.length > 0
      ) {
        // Show upload all button or automatically upload
        this.showDualUploadReady();
      }
    } catch (error) {
      const statusId = isJob ? "job-status" : "resume-status";
      const areaId = isJob ? "job-upload-area" : "resume-upload-area";

      document.getElementById(areaId).classList.add("error");
      document.getElementById(statusId).innerHTML = `
        <i class="fas fa-exclamation-circle text-danger me-1"></i>
        <span class="status-error">File selection failed: ${error.message}</span>
      `;
    }
  }

  showDualUploadReady() {
    // Add upload all button if not exists
    let uploadAllBtn = document.getElementById("upload-all-btn");
    if (!uploadAllBtn) {
      uploadAllBtn = document.createElement("button");
      uploadAllBtn.id = "upload-all-btn";
      uploadAllBtn.className = "btn btn-primary btn-lg mt-3";
      uploadAllBtn.innerHTML =
        '<i class="fas fa-cloud-upload-alt me-2"></i>Upload All Files';
      uploadAllBtn.onclick = () => this.performDualUpload();

      // Insert after upload areas
      const uploadSection = document.querySelector(".row:has(.upload-area)");
      uploadSection.parentNode.insertBefore(
        uploadAllBtn,
        uploadSection.nextSibling
      );
    }

    uploadAllBtn.style.display = "block";
    uploadAllBtn.disabled = false;
  }

  async performDualUpload() {
    if (
      !this.dualUpload.pendingJobFiles?.length ||
      !this.dualUpload.pendingResumeFiles?.length
    ) {
      this.showError("Need both job descriptions and resumes for dual upload");
      return;
    }

    this.showLoading(true, "Uploading files...");

    try {
      const result = await this.handleDualUpload(
        this.dualUpload.pendingJobFiles,
        this.dualUpload.pendingResumeFiles
      );

      // Clear pending files
      this.dualUpload.pendingJobFiles = [];
      this.dualUpload.pendingResumeFiles = [];

      // Hide upload button
      const uploadAllBtn = document.getElementById("upload-all-btn");
      if (uploadAllBtn) uploadAllBtn.style.display = "none";

      this.showSuccess(
        `Successfully uploaded ${result.summary.total_resumes} resumes and ${result.summary.total_job_descriptions} job descriptions`
      );
    } catch (error) {
      this.log("Dual upload failed:", error);
      this.showError(`Dual upload failed: ${error.message}`);
    } finally {
      this.showLoading(false);
    }
  }

  async uploadFile(file, isJob) {
    this.log(`Uploading ${isJob ? "job description" : "resume"}: ${file.name}`);

    const formData = new FormData();
    formData.append("file", file);

    const endpoint = isJob
      ? "/api/upload/job-description"
      : "/api/upload/resume";

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      this.log("Upload response:", result);

      if (!response.ok) {
        throw new Error(result.error || "Upload failed");
      }

      // Ensure we have all required fields
      if (!result.file_id) {
        throw new Error("Upload response missing file_id");
      }

      const fileData = {
        file_id: result.file_id,
        filename: result.filename || file.name,
        size: file.size,
        success: true,
        message: result.message,
      };

      this.log("File uploaded successfully:", fileData);
      return fileData;
    } catch (error) {
      this.log("Upload failed:", error);
      throw new Error(`Upload failed: ${error.message}`);
    }
  }

  // Enhanced dual upload methods
  async handleDualUpload(jobFiles, resumeFiles) {
    this.log("Starting dual upload process...", {
      jobs: jobFiles.length,
      resumes: resumeFiles.length,
    });

    const formData = new FormData();

    // Add job description files
    jobFiles.forEach((file) => {
      formData.append("job_description_files", file);
    });

    // Add resume files
    resumeFiles.forEach((file) => {
      formData.append("resume_files", file);
    });

    try {
      const response = await fetch("/api/upload/dual", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || "Dual upload failed");
      }

      this.log("Dual upload successful:", result);

      // Update internal state
      this.dualUpload.jobDescriptions = result.files.job_descriptions || [];
      this.dualUpload.resumes = result.files.resumes || [];

      // Update UI
      this.updateDualUploadStatus();
      this.updateAnalysisMatrix();

      return result;
    } catch (error) {
      this.log("Dual upload failed:", error);
      throw error;
    }
  }

  async performBatchProcessing() {
    this.log("Starting batch processing and analysis...");

    if (
      this.dualUpload.jobDescriptions.length === 0 ||
      this.dualUpload.resumes.length === 0
    ) {
      throw new Error(
        "Need at least one job description and one resume for batch processing"
      );
    }

    const formData = new FormData();

    // Add files (they should already be uploaded)
    this.dualUpload.jobDescriptions.forEach((job) => {
      const fileInput = document.createElement("input");
      fileInput.type = "hidden";
      fileInput.name = "job_description_ids";
      fileInput.value = job.file_id;
      formData.append("job_description_ids", job.file_id);
    });

    this.dualUpload.resumes.forEach((resume) => {
      formData.append("resume_ids", resume.file_id);
    });

    // Add analysis options
    const options = this.getAnalysisOptions();
    Object.entries(options).forEach(([key, value]) => {
      formData.append(key, value);
    });

    try {
      const response = await fetch("/api/upload/batch-process", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || "Batch processing failed");
      }

      this.log("Batch processing successful:", result);

      // Update results
      if (result.analysis_results && result.analysis_results.results) {
        this.analysisResults = this.formatDualAnalysisResults(
          result.analysis_results.results
        );
        this.displayDualAnalysisResults();
      }

      return result;
    } catch (error) {
      this.log("Batch processing failed:", error);
      throw error;
    }
  }

  async performDualAnalysis() {
    this.log("Performing dual analysis...");

    if (
      this.dualUpload.jobDescriptions.length === 0 ||
      this.dualUpload.resumes.length === 0
    ) {
      throw new Error(
        "Need at least one job description and one resume for analysis"
      );
    }

    const analysisData = {
      resume_ids: this.dualUpload.resumes.map((r) => r.file_id),
      job_description_ids: this.dualUpload.jobDescriptions.map(
        (j) => j.file_id
      ),
      options: this.getAnalysisOptions(),
    };

    try {
      const response = await fetch("/api/evaluate/dual-upload", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(analysisData),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || "Dual analysis failed");
      }

      this.log("Dual analysis successful:", result);

      // Store and display results
      this.dualUpload.currentAnalysis = result;
      this.analysisResults = this.formatDualAnalysisResults(result.results);
      this.displayDualAnalysisResults();

      return result;
    } catch (error) {
      this.log("Dual analysis failed:", error);
      throw error;
    }
  }

  getAnalysisOptions() {
    return {
      include_skills:
        document.getElementById("include-skills")?.checked ?? true,
      include_experience:
        document.getElementById("include-experience")?.checked ?? true,
      include_semantic:
        document.getElementById("include-semantic")?.checked ?? true,
      include_keywords: true,
      generate_recommendations: true,
      detailed_feedback:
        document.getElementById("include-feedback")?.checked ?? true,
      include_comparison:
        document.getElementById("include-comparison")?.checked ?? true,
      cross_analysis:
        document.getElementById("cross-analysis")?.checked ?? true,
    };
  }

  formatDualAnalysisResults(results) {
    return results
      .filter((r) => r.status === "success")
      .map((result) => {
        const analysis = result.analysis;

        return {
          id: `${result.resume_id}_${result.job_description_id}`,
          candidate: {
            id: result.resume_id,
            filename: result.metadata?.resume_filename || result.resume_id,
          },
          job_description: {
            id: result.job_description_id,
            filename:
              result.metadata?.job_desc_filename || result.job_description_id,
          },
          relevance_score: analysis.overall_score * 100,
          skill_match_percentage:
            analysis.skill_analysis?.match_percentage || 0,
          matching_skills: analysis.skill_analysis?.matched_skills || [],
          missing_skills: analysis.skill_analysis?.missing_skills || [],
          recommendations: analysis.recommendations || [],
          feedback: result.feedback,
          processing_time: result.metadata?.processing_time || 0,
          analysis_timestamp: result.metadata?.analysis_timestamp,
        };
      });
  }

  updateDualUploadStatus() {
    // Update job descriptions count and list
    const jobCountEl = document.getElementById("job-count");
    const jobListEl = document.getElementById("job-descriptions-list");

    if (jobCountEl)
      jobCountEl.textContent = this.dualUpload.jobDescriptions.length;

    if (jobListEl) {
      jobListEl.innerHTML = this.dualUpload.jobDescriptions
        .map(
          (job) => `
        <div class="file-item">
          <i class="fas fa-file-alt me-2"></i>
          <span class="file-name">${job.original_name || job.filename}</span>
          <button class="btn btn-sm btn-outline-danger ms-2" onclick="dashboard.removeJobDescription('${
            job.file_id
          }')">
            <i class="fas fa-times"></i>
          </button>
        </div>
      `
        )
        .join("");
    }

    // Update resumes count and list
    const resumeCountEl = document.getElementById("resume-count");
    const resumeListEl = document.getElementById("resumes-list");

    if (resumeCountEl)
      resumeCountEl.textContent = this.dualUpload.resumes.length;

    if (resumeListEl) {
      resumeListEl.innerHTML = this.dualUpload.resumes
        .map(
          (resume) => `
        <div class="file-item">
          <i class="fas fa-file-pdf me-2"></i>
          <span class="file-name">${
            resume.original_name || resume.filename
          }</span>
          <button class="btn btn-sm btn-outline-danger ms-2" onclick="dashboard.removeResume('${
            resume.file_id
          }')">
            <i class="fas fa-times"></i>
          </button>
        </div>
      `
        )
        .join("");
    }
  }

  updateAnalysisMatrix() {
    const matrixEl = document.getElementById("analysis-matrix");
    const matrixContentEl = document.getElementById("matrix-content");

    if (!matrixEl || !matrixContentEl) return;

    if (
      this.dualUpload.jobDescriptions.length > 0 &&
      this.dualUpload.resumes.length > 0
    ) {
      matrixEl.style.display = "block";

      const totalCombinations =
        this.dualUpload.jobDescriptions.length * this.dualUpload.resumes.length;

      matrixContentEl.innerHTML = `
        <div class="matrix-info">
          <div class="row text-center">
            <div class="col-4">
              <div class="metric-card">
                <h4>${this.dualUpload.jobDescriptions.length}</h4>
                <small>Job Descriptions</small>
              </div>
            </div>
            <div class="col-4">
              <div class="metric-card">
                <h4>×</h4>
                <small>Cross Analysis</small>
              </div>
            </div>
            <div class="col-4">
              <div class="metric-card">
                <h4>${this.dualUpload.resumes.length}</h4>
                <small>Resumes</small>
              </div>
            </div>
          </div>
          <div class="text-center mt-3">
            <span class="badge bg-primary fs-6">
              ${totalCombinations} Total Combinations to Analyze
            </span>
          </div>
        </div>
      `;
    } else {
      matrixEl.style.display = "none";
    }
  }

  displayDualAnalysisResults() {
    this.log("Displaying dual analysis results...", this.analysisResults);

    // Use existing display methods but enhance them for dual mode
    this.displayResults();

    // Add dual-specific summary
    if (this.dualUpload.currentAnalysis?.summary) {
      this.displayDualAnalysisSummary(this.dualUpload.currentAnalysis.summary);
    }
  }

  displayDualAnalysisSummary(summary) {
    const summaryHtml = `
      <div class="dual-analysis-summary mb-4">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-gradient-success text-white">
            <h6 class="mb-0">
              <i class="fas fa-chart-line me-2"></i>Dual Analysis Summary
            </h6>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-3">
                <div class="summary-metric">
                  <h4>${summary.total_combinations}</h4>
                  <small>Total Combinations</small>
                </div>
              </div>
              <div class="col-md-3">
                <div class="summary-metric">
                  <h4>${summary.successful_analyses}</h4>
                  <small>Successful Analyses</small>
                </div>
              </div>
              <div class="col-md-3">
                <div class="summary-metric">
                  <h4>${summary.success_rate.toFixed(1)}%</h4>
                  <small>Success Rate</small>
                </div>
              </div>
              <div class="col-md-3">
                <div class="summary-metric">
                  <h4>${summary.total_processing_time.toFixed(2)}s</h4>
                  <small>Processing Time</small>
                </div>
              </div>
            </div>
            ${
              summary.comparison
                ? `
              <div class="comparison-summary mt-3">
                <h6>Score Distribution</h6>
                <div class="row">
                  <div class="col-4 text-center">
                    <span class="badge bg-success fs-6">${
                      summary.comparison.score_distribution.high
                    } High (≥80%)</span>
                  </div>
                  <div class="col-4 text-center">
                    <span class="badge bg-warning fs-6">${
                      summary.comparison.score_distribution.medium
                    } Medium (50-79%)</span>
                  </div>
                  <div class="col-4 text-center">
                    <span class="badge bg-danger fs-6">${
                      summary.comparison.score_distribution.low
                    } Low (<50%)</span>
                  </div>
                </div>
                <div class="mt-2 text-center">
                  <small>Average Score: ${summary.comparison.average_score.toFixed(
                    1
                  )}%</small>
                </div>
              </div>
            `
                : ""
            }
          </div>
        </div>
      </div>
    `;

    // Insert before results
    const resultsSection = document.getElementById("results-section");
    if (resultsSection) {
      const existingSummary = resultsSection.querySelector(
        ".dual-analysis-summary"
      );
      if (existingSummary) {
        existingSummary.remove();
      }
      resultsSection.insertAdjacentHTML("afterbegin", summaryHtml);
    }
  }

  removeJobDescription(fileId) {
    this.dualUpload.jobDescriptions = this.dualUpload.jobDescriptions.filter(
      (job) => job.file_id !== fileId
    );
    this.updateDualUploadStatus();
    this.updateAnalysisMatrix();
  }

  removeResume(fileId) {
    this.dualUpload.resumes = this.dualUpload.resumes.filter(
      (resume) => resume.file_id !== fileId
    );
    this.updateDualUploadStatus();
    this.updateAnalysisMatrix();
  }

  updateAnalyzeButton() {
    const btn = document.getElementById("analyze-btn");
    if (this.jobFile && this.resumeFiles.length > 0) {
      btn.disabled = false;
      btn.innerHTML = `<i class="fas fa-search me-2"></i>Analyze ${this.resumeFiles.length} Resume(s)`;
    } else {
      btn.disabled = true;
      btn.innerHTML =
        '<i class="fas fa-search me-2"></i>Upload files to analyze';
    }
  }

  async analyzeResumes() {
    this.log("Starting resume analysis...", { mode: this.dualUpload.mode });

    // Handle different upload modes
    if (this.dualUpload.mode === "dual") {
      return await this.performDualAnalysis();
    } else if (this.dualUpload.mode === "batch") {
      return await this.performBatchProcessing();
    }

    // Standard mode validation and analysis
    if (!this.jobFile || this.resumeFiles.length === 0) {
      const errorMsg = "Please upload both job description and resume(s)";
      this.log("Analysis validation failed:", errorMsg);
      this.showError(errorMsg);
      return;
    }

    // Validate file data integrity
    if (!this.jobFile.file_id) {
      this.showError("Job description file data is invalid. Please re-upload.");
      return;
    }

    for (const resume of this.resumeFiles) {
      if (!resume.file_id) {
        this.showError(
          "One or more resume files are invalid. Please re-upload."
        );
        return;
      }
    }

    this.showLoading(true);
    this.analysisResults = [];
    let successCount = 0;
    let errorCount = 0;

    try {
      this.log(
        `Analyzing ${this.resumeFiles.length} resumes against job: ${this.jobFile.filename}`
      );

      for (const resume of this.resumeFiles) {
        try {
          const result = await this.analyzeResume(resume);
          if (result) {
            this.analysisResults.push(result);
            successCount++;
            this.log(`Successfully analyzed: ${resume.filename}`);
          }
        } catch (error) {
          errorCount++;
          this.log(`Failed to analyze ${resume.filename}:`, error);
          // Continue with other resumes instead of stopping
          this.showError(
            `Failed to analyze ${resume.filename}: ${error.message}`
          );
        }
      }

      if (successCount > 0) {
        this.displayResults();
        this.updateCharts();
        this.log(
          `Analysis complete: ${successCount} successful, ${errorCount} failed`
        );

        if (errorCount > 0) {
          this.showError(
            `Analysis completed with ${errorCount} errors. Check console for details.`
          );
        }
      } else {
        throw new Error(
          "All resume analyses failed. Please check your files and try again."
        );
      }
    } catch (error) {
      this.log("Analysis failed completely:", error);
      this.showError("Analysis failed: " + error.message);
    } finally {
      this.showLoading(false);
    }
  }

  async analyzeResume(resume) {
    this.log(`Analyzing resume: ${resume.filename} (ID: ${resume.file_id})`);

    const requestBody = {
      resume_id: resume.file_id,
      job_description_id: this.jobFile.file_id,
    };

    this.log("API request body:", requestBody);

    try {
      const response = await fetch("/api/evaluate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      this.log(`API response status: ${response.status}`);

      const result = await response.json();
      this.log("API response data:", result);

      if (!response.ok) {
        throw new Error(
          result.error ||
            `API returned ${response.status}: ${response.statusText}`
        );
      }

      // Validate response structure
      if (typeof result.relevance_score === "undefined") {
        this.log("Warning: API response missing expected fields", result);
        // Still try to process it, might have different structure
      }

      const analysisResult = {
        ...result,
        candidate: {
          id: resume.file_id,
          filename: resume.filename,
          size: resume.size || 0,
        },
        // Ensure required fields exist with defaults
        relevance_score: result.relevance_score || 0,
        relevance_level: result.relevance_level || "Unknown",
        matching_skills: result.matching_skills || [],
        missing_skills: result.missing_skills || [],
        timestamp: new Date().toISOString(),
      };

      this.log("Processed analysis result:", analysisResult);
      return analysisResult;
    } catch (error) {
      this.log(`Analysis failed for ${resume.filename}:`, error);
      throw new Error(`Failed to analyze ${resume.filename}: ${error.message}`);
    }
  }

  displayResults() {
    const container = document.getElementById("results-container");

    if (this.analysisResults.length === 0) {
      container.innerHTML = `
                <div class="text-center text-muted py-5">
                    <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
                    <p class="lead">No results to display</p>
                </div>
            `;
      return;
    }

    // Sort results by relevance score
    const sortedResults = [...this.analysisResults].sort(
      (a, b) => b.relevance_score - a.relevance_score
    );

    container.innerHTML = `
            <div class="row g-3">
                ${sortedResults
                  .map((result) => this.createResultCard(result))
                  .join("")}
            </div>
        `;

    this.updateCandidatesTable();
  }

  createResultCard(result) {
    const relevanceClass = this.getRelevanceClass(result.relevance_score);
    const scoreClass = this.getScoreClass(result.relevance_score);

    return `
            <div class="col-md-6 col-lg-4">
                <div class="card result-card ${relevanceClass} fade-in">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <h6 class="card-title mb-0">${
                              result.candidate.filename
                            }</h6>
                            <span class="score-badge ${scoreClass}">${result.relevance_score.toFixed(
      1
    )}%</span>
                        </div>
                        
                        <div class="mb-3">
                            <small class="text-muted">Skill Match</small>
                            <div class="progress mt-1" style="height: 8px;">
                                <div class="progress-bar bg-info" style="width: ${
                                  result.skill_match_percentage
                                }%"></div>
                            </div>
                            <small class="text-muted">${result.skill_match_percentage.toFixed(
                              1
                            )}%</small>
                        </div>
                        
                        <div class="mb-3">
                            <small class="text-muted d-block mb-1">Matching Skills (${
                              result.matching_skills.length
                            })</small>
                            <div class="skill-tags">
                                ${result.matching_skills
                                  .slice(0, 5)
                                  .map(
                                    (skill) =>
                                      `<span class="skill-tag skill-matched">${skill}</span>`
                                  )
                                  .join("")}
                                ${
                                  result.matching_skills.length > 5
                                    ? `<span class="skill-tag skill-matched">+${
                                        result.matching_skills.length - 5
                                      } more</span>`
                                    : ""
                                }
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <small class="text-muted d-block mb-1">Missing Skills (${
                              result.missing_skills.length
                            })</small>
                            <div class="skill-tags">
                                ${result.missing_skills
                                  .slice(0, 3)
                                  .map(
                                    (skill) =>
                                      `<span class="skill-tag skill-missing">${skill}</span>`
                                  )
                                  .join("")}
                                ${
                                  result.missing_skills.length > 3
                                    ? `<span class="skill-tag skill-missing">+${
                                        result.missing_skills.length - 3
                                      } more</span>`
                                    : ""
                                }
                            </div>
                        </div>
                        
                        <button class="btn btn-sm btn-outline-primary w-100" 
                                onclick="dashboard.showCandidateDetails('${
                                  result.candidate.id
                                }')">
                            <i class="fas fa-eye me-1"></i>View Details
                        </button>
                    </div>
                </div>
            </div>
        `;
  }

  updateCandidatesTable() {
    const tbody = document.getElementById("candidates-tbody");
    const sortedResults = this.getSortedResults();

    // Calculate pagination
    const totalItems = sortedResults.length;
    this.pagination.totalPages = Math.ceil(
      totalItems / this.pagination.itemsPerPage
    );

    // Ensure current page is valid
    if (this.pagination.currentPage > this.pagination.totalPages) {
      this.pagination.currentPage = 1;
    }

    if (totalItems === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" class="text-center text-muted py-4">
            <i class="fas fa-search fa-2x mb-3"></i>
            <div>No candidates analyzed yet</div>
            <small>Upload job description and resumes to begin analysis</small>
          </td>
        </tr>
      `;
      this.updatePaginationControls(0);
      return;
    }

    // Calculate pagination slice
    const startIndex =
      (this.pagination.currentPage - 1) * this.pagination.itemsPerPage;
    const endIndex = startIndex + this.pagination.itemsPerPage;
    const paginatedResults = sortedResults.slice(startIndex, endIndex);

    tbody.innerHTML = paginatedResults
      .map(
        (result) => `
            <tr>
                <td>
                    <div class="d-flex align-items-center">
                        <i class="fas fa-user-circle text-muted me-2"></i>
                        <div>
                            <div class="fw-medium">${
                              result.candidate.filename
                            }</div>
                            <small class="text-muted">${this.formatFileSize(
                              result.candidate.size
                            )}</small>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="score-badge ${this.getScoreClass(
                      result.relevance_score
                    )}" style="font-size: 0.9rem;">
                        ${result.relevance_score.toFixed(1)}%
                    </span>
                    <div class="mt-1">
                        <small class="text-muted">${
                          result.relevance_level
                        }</small>
                    </div>
                </td>
                <td>
                    <div class="progress" style="height: 6px;">
                        <div class="progress-bar bg-info" style="width: ${
                          result.skill_match_percentage
                        }%"></div>
                    </div>
                    <small class="text-muted">${result.skill_match_percentage.toFixed(
                      1
                    )}%</small>
                </td>
                <td>
                    <span class="badge bg-danger me-2">${
                      result.missing_skills.length
                    }</span>
                    ${result.missing_skills
                      .slice(0, 2)
                      .map(
                        (skill) =>
                          `<span class="skill-tag skill-missing ms-1">${skill}</span>`
                      )
                      .join("")}
                    ${
                      result.missing_skills.length > 2
                        ? `<small class="text-muted">+${
                            result.missing_skills.length - 2
                          } more</small>`
                        : ""
                    }
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="dashboard.showCandidateDetails('${
                          result.candidate.id
                        }')" title="View Details">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-outline-success" onclick="dashboard.generateDetailedReport('${
                          result.candidate.id
                        }')" title="Generate Report">
                            <i class="fas fa-file-alt"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `
      )
      .join("");

    this.updatePaginationControls(totalItems);
  }

  updatePaginationControls(totalItems) {
    const paginationContainer =
      document.getElementById("pagination-container") ||
      this.createPaginationContainer();

    if (totalItems <= this.pagination.itemsPerPage) {
      paginationContainer.style.display = "none";
      return;
    }

    paginationContainer.style.display = "flex";

    const { currentPage, totalPages, itemsPerPage } = this.pagination;
    const startItem = (currentPage - 1) * itemsPerPage + 1;
    const endItem = Math.min(currentPage * itemsPerPage, totalItems);

    paginationContainer.innerHTML = `
      <div class="d-flex justify-content-between align-items-center w-100">
        <div class="text-muted">
          Showing ${startItem}-${endItem} of ${totalItems} candidates
        </div>
        
        <nav>
          <ul class="pagination pagination-sm mb-0">
            <li class="page-item ${currentPage === 1 ? "disabled" : ""}">
              <button class="page-link" onclick="dashboard.goToPage(${
                currentPage - 1
              })" ${currentPage === 1 ? "disabled" : ""}>
                <i class="fas fa-chevron-left"></i>
              </button>
            </li>
            
            ${this.generatePageNumbers()
              .map(
                (page) => `
              <li class="page-item ${page === currentPage ? "active" : ""} ${
                  typeof page === "string" ? "disabled" : ""
                }">
                <button class="page-link" ${
                  typeof page === "string"
                    ? "disabled"
                    : `onclick="dashboard.goToPage(${page})"`
                }>
                  ${page}
                </button>
              </li>
            `
              )
              .join("")}
            
            <li class="page-item ${
              currentPage === totalPages ? "disabled" : ""
            }">
              <button class="page-link" onclick="dashboard.goToPage(${
                currentPage + 1
              })" ${currentPage === totalPages ? "disabled" : ""}>
                <i class="fas fa-chevron-right"></i>
              </button>
            </li>
          </ul>
        </nav>
        
        <div class="d-flex align-items-center">
          <label class="me-2 text-muted">Per page:</label>
          <select class="form-select form-select-sm" style="width: auto;" onchange="dashboard.changeItemsPerPage(this.value)">
            <option value="5" ${itemsPerPage === 5 ? "selected" : ""}>5</option>
            <option value="10" ${
              itemsPerPage === 10 ? "selected" : ""
            }>10</option>
            <option value="25" ${
              itemsPerPage === 25 ? "selected" : ""
            }>25</option>
            <option value="50" ${
              itemsPerPage === 50 ? "selected" : ""
            }>50</option>
          </select>
        </div>
      </div>
    `;
  }

  generatePageNumbers() {
    const { currentPage, totalPages } = this.pagination;
    const pages = [];

    if (totalPages <= 7) {
      // Show all pages if 7 or fewer
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Complex pagination with ellipsis
      if (currentPage <= 4) {
        pages.push(1, 2, 3, 4, 5, "...", totalPages);
      } else if (currentPage >= totalPages - 3) {
        pages.push(
          1,
          "...",
          totalPages - 4,
          totalPages - 3,
          totalPages - 2,
          totalPages - 1,
          totalPages
        );
      } else {
        pages.push(
          1,
          "...",
          currentPage - 1,
          currentPage,
          currentPage + 1,
          "...",
          totalPages
        );
      }
    }

    return pages;
  }

  createPaginationContainer() {
    const existingTable = document
      .querySelector("#candidates-tbody")
      .closest("table");
    const container = document.createElement("div");
    container.id = "pagination-container";
    container.className = "d-flex justify-content-center mt-3";
    existingTable.parentNode.insertBefore(container, existingTable.nextSibling);
    return container;
  }

  goToPage(page) {
    if (page < 1 || page > this.pagination.totalPages) return;
    this.pagination.currentPage = page;
    this.updateCandidatesTable();
  }

  changeItemsPerPage(itemsPerPage) {
    this.pagination.itemsPerPage = parseInt(itemsPerPage);
    this.pagination.currentPage = 1; // Reset to first page
    this.updateCandidatesTable();
  }

  initializeCharts() {
    this.log("Initializing charts...");

    // Check if Chart.js is available
    if (typeof Chart === "undefined") {
      const errorMsg = "Chart.js is not loaded. Charts will not be available.";
      console.error(errorMsg);
      this.log(errorMsg);
      // Show user-friendly message instead of failing silently
      const chartContainers = document.querySelectorAll(".chart-container");
      chartContainers.forEach((container) => {
        container.innerHTML = `
          <div class="text-center text-muted py-4">
            <i class="fas fa-chart-bar fa-2x mb-2"></i>
            <p>Chart functionality unavailable</p>
            <small>Chart.js library failed to load</small>
          </div>
        `;
      });
      return;
    }

    try {
      let chartsCreated = 0;

      // Skill Gap Chart (Pie)
      const skillGapCtx = document.getElementById("skill-gap-chart");
      if (skillGapCtx) {
        this.charts.skillGap = new Chart(skillGapCtx, {
          type: "pie",
          data: {
            labels: ["Matching Skills", "Missing Skills"],
            datasets: [
              {
                data: [0, 0],
                backgroundColor: ["#198754", "#dc3545"],
                borderWidth: 2,
                borderColor: "#fff",
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: "bottom",
              },
              tooltip: {
                callbacks: {
                  label: (context) => {
                    const total = context.dataset.data.reduce(
                      (a, b) => a + b,
                      0
                    );
                    if (total === 0) return `${context.label}: 0`;
                    const percentage = ((context.raw / total) * 100).toFixed(1);
                    return `${context.label}: ${context.raw} (${percentage}%)`;
                  },
                },
              },
            },
          },
        });
        chartsCreated++;
        this.log("Skill gap chart created");
      } else {
        this.log("Warning: skill-gap-chart element not found");
      }

      // Missing Skills Chart (Bar)
      const missingSkillsCtx = document.getElementById("missing-skills-chart");
      if (missingSkillsCtx) {
        this.charts.missingSkills = new Chart(missingSkillsCtx, {
          type: "bar",
          data: {
            labels: [],
            datasets: [
              {
                label: "Frequency",
                data: [],
                backgroundColor: "#dc3545",
                borderColor: "#dc3545",
                borderWidth: 1,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  stepSize: 1,
                },
              },
            },
            plugins: {
              legend: {
                display: false,
              },
            },
          },
        });
        chartsCreated++;
        this.log("Missing skills chart created");
      } else {
        this.log("Warning: missing-skills-chart element not found");
      }

      // Score Distribution Chart (Histogram)
      const scoreDistCtx = document.getElementById("score-distribution-chart");
      if (scoreDistCtx) {
        this.charts.scoreDistribution = new Chart(scoreDistCtx, {
          type: "bar",
          data: {
            labels: ["0-20%", "21-40%", "41-60%", "61-80%", "81-100%"],
            datasets: [
              {
                label: "Number of Candidates",
                data: [0, 0, 0, 0, 0],
                backgroundColor: [
                  "#dc3545",
                  "#fd7e14",
                  "#ffc107",
                  "#198754",
                  "#20c997",
                ],
                borderWidth: 1,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  stepSize: 1,
                },
              },
            },
            plugins: {
              legend: {
                display: false,
              },
            },
          },
        });
        chartsCreated++;
        this.log("Score distribution chart created");
      } else {
        this.log("Warning: score-distribution-chart element not found");
      }

      this.log(
        `Charts initialization complete: ${chartsCreated} charts created`
      );
    } catch (error) {
      console.error("Error initializing charts:", error);
      this.log("Chart initialization failed:", error);

      // Show user-friendly error message
      const chartContainers = document.querySelectorAll(".chart-container");
      chartContainers.forEach((container) => {
        if (!container.querySelector("canvas")) return; // Skip if already has content
        container.innerHTML = `
          <div class="text-center text-muted py-4">
            <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
            <p>Chart initialization failed</p>
            <small>${error.message}</small>
          </div>
        `;
      });
    }
  }

  updateCharts() {
    try {
      this.log(
        "Starting chart updates with analysis results:",
        this.analysisResults.length
      );

      if (this.analysisResults.length === 0) {
        this.log("No analysis results available for chart updates");
        this.clearCharts();
        return;
      }

      // Update Skill Gap Chart
      if (this.charts.skillGap) {
        try {
          const totalMatching = this.analysisResults.reduce(
            (sum, result) => sum + (result.matching_skills?.length || 0),
            0
          );
          const totalMissing = this.analysisResults.reduce(
            (sum, result) => sum + (result.missing_skills?.length || 0),
            0
          );

          this.charts.skillGap.data.datasets[0].data = [
            totalMatching,
            totalMissing,
          ];
          this.charts.skillGap.update();
          this.log(
            `Skill gap chart updated: matching=${totalMatching}, missing=${totalMissing}`
          );
        } catch (error) {
          console.error("Error updating skill gap chart:", error);
          this.log("Failed to update skill gap chart:", error.message);
        }
      } else {
        this.log("Warning: Skill gap chart not available");
      }

      // Update Missing Skills Chart
      if (this.charts.missingSkills) {
        try {
          const missingSkillsCount = {};
          this.analysisResults.forEach((result) => {
            const skills = result.missing_skills || [];
            if (Array.isArray(skills)) {
              skills.forEach((skill) => {
                if (typeof skill === "string" && skill.trim()) {
                  missingSkillsCount[skill] =
                    (missingSkillsCount[skill] || 0) + 1;
                }
              });
            }
          });

          const topMissingSkills = Object.entries(missingSkillsCount)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 8);

          this.charts.missingSkills.data.labels = topMissingSkills.map(
            ([skill]) => skill
          );
          this.charts.missingSkills.data.datasets[0].data =
            topMissingSkills.map(([, count]) => count);
          this.charts.missingSkills.update();
          this.log(
            `Missing skills chart updated with ${topMissingSkills.length} skills`
          );
        } catch (error) {
          console.error("Error updating missing skills chart:", error);
          this.log("Failed to update missing skills chart:", error.message);
        }
      } else {
        this.log("Warning: Missing skills chart not available");
      }

      // Update Score Distribution Chart
      if (this.charts.scoreDistribution) {
        try {
          const scoreRanges = [0, 0, 0, 0, 0];
          this.analysisResults.forEach((result) => {
            const score = parseFloat(result.relevance_score) || 0;
            if (score <= 20) scoreRanges[0]++;
            else if (score <= 40) scoreRanges[1]++;
            else if (score <= 60) scoreRanges[2]++;
            else if (score <= 80) scoreRanges[3]++;
            else scoreRanges[4]++;
          });

          this.charts.scoreDistribution.data.datasets[0].data = scoreRanges;
          this.charts.scoreDistribution.update();
          this.log("Score distribution chart updated:", scoreRanges);
        } catch (error) {
          console.error("Error updating score distribution chart:", error);
          this.log("Failed to update score distribution chart:", error.message);
        }
      } else {
        this.log("Warning: Score distribution chart not available");
      }

      this.log("Chart updates completed successfully");
    } catch (error) {
      console.error("Error updating charts:", error);
      this.log("Chart update failed:", error.message);
    }
  }

  clearCharts() {
    try {
      this.log("Clearing all charts");

      Object.keys(this.charts).forEach((chartKey) => {
        const chart = this.charts[chartKey];
        if (chart && chart.data) {
          // Clear data for different chart types
          if (chart.data.datasets) {
            chart.data.datasets.forEach((dataset) => {
              if (Array.isArray(dataset.data)) {
                dataset.data.length = 0;
              }
            });
          }
          if (chart.data.labels) {
            chart.data.labels.length = 0;
          }
          chart.update();
          this.log(`Cleared chart: ${chartKey}`);
        }
      });
    } catch (error) {
      console.error("Error clearing charts:", error);
      this.log("Failed to clear charts:", error.message);
    }
  }

  getSortedResults() {
    try {
      this.log("Getting sorted results");

      const sortByElement = document.getElementById("sort-candidates");
      const sortBy = sortByElement ? sortByElement.value : "relevance_score";
      const results = [...this.analysisResults];

      results.sort((a, b) => {
        try {
          switch (sortBy) {
            case "relevance_score":
              const aScore = parseFloat(a.relevance_score) || 0;
              const bScore = parseFloat(b.relevance_score) || 0;
              return bScore - aScore; // Descending

            case "skill_match":
              const aSkillMatch = parseFloat(a.skill_match_percentage) || 0;
              const bSkillMatch = parseFloat(b.skill_match_percentage) || 0;
              return bSkillMatch - aSkillMatch; // Descending

            case "filename":
              const aFilename = (a.candidate?.filename || "").toLowerCase();
              const bFilename = (b.candidate?.filename || "").toLowerCase();
              return aFilename.localeCompare(bFilename); // Ascending

            default:
              this.log("Unknown sort criteria:", sortBy);
              return 0;
          }
        } catch (error) {
          console.error("Error in sort comparison:", error);
          return 0;
        }
      });

      this.log(`Sorted ${results.length} results by ${sortBy}`);
      return results;
    } catch (error) {
      console.error("Error sorting results:", error);
      this.log("Failed to sort results:", error.message);
      return this.analysisResults || [];
    }
  }

  showCandidateDetails(candidateId) {
    try {
      this.log("Showing candidate details for ID:", candidateId);

      const result = this.analysisResults.find(
        (r) => r.candidate?.id === candidateId
      );

      if (!result) {
        this.log("Candidate not found with ID:", candidateId);
        this.showError("Candidate details not found");
        return;
      }

      const modalBody = document.getElementById("candidate-details");
      if (!modalBody) {
        this.log("Modal body element not found");
        this.showError(
          "Cannot display candidate details - modal not available"
        );
        return;
      }

      // Safely get values with defaults
      const filename = result.candidate?.filename || "Unknown";
      const fileSize = result.candidate?.size || 0;
      const relevanceLevel = result.relevance_level || "Unknown";
      const relevanceScore = parseFloat(result.relevance_score) || 0;
      const skillMatchPercentage =
        parseFloat(result.skill_match_percentage) || 0;
      const matchingSkills = Array.isArray(result.matching_skills)
        ? result.matching_skills
        : [];
      const missingSkills = Array.isArray(result.missing_skills)
        ? result.missing_skills
        : [];
      const totalJobSkills = result.total_job_skills || 0;
      const recommendations = Array.isArray(result.recommendations)
        ? result.recommendations
        : [];

      modalBody.innerHTML = `
        <div class="row g-4">
            <div class="col-md-6">
                <div class="card border-0 bg-light">
                    <div class="card-body">
                        <h6 class="card-title">
                            <i class="fas fa-user me-2"></i>Candidate Information
                        </h6>
                        <div class="mb-2">
                            <strong>Filename:</strong> ${this.escapeHtml(
                              filename
                            )}
                        </div>
                        <div class="mb-2">
                            <strong>File Size:</strong> ${this.formatFileSize(
                              fileSize
                            )}
                        </div>
                        <div class="mb-2">
                            <strong>Relevance Level:</strong> 
                            <span class="badge ${this.getRelevanceBadgeClass(
                              relevanceLevel
                            )}">${this.escapeHtml(relevanceLevel)}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card border-0 bg-light">
                    <div class="card-body">
                        <h6 class="card-title">
                            <i class="fas fa-chart-bar me-2"></i>Scores & Metrics
                        </h6>
                        
                        ${this.createProgressBar(
                          relevanceScore,
                          "Relevance Score",
                          this.getProgressBarColorClass(relevanceScore)
                        )}
                        ${this.createProgressBar(
                          skillMatchPercentage,
                          "Skill Match",
                          "info"
                        )}
                        
                        <div class="row text-center mt-3">
                            <div class="col">
                                <div class="text-success fw-bold fs-4">${
                                  matchingSkills.length
                                }</div>
                                <small class="text-muted">Matched</small>
                            </div>
                            <div class="col">
                                <div class="text-danger fw-bold fs-4">${
                                  missingSkills.length
                                }</div>
                                <small class="text-muted">Missing</small>
                            </div>
                            <div class="col">
                                <div class="text-primary fw-bold fs-4">${totalJobSkills}</div>
                                <small class="text-muted">Required</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-12">
                <div class="accordion" id="candidateDetailsAccordion">
                    ${this.createCollapsiblePanel(
                      `<i class="fas fa-check-circle text-success me-2"></i>Matching Skills (${matchingSkills.length})`,
                      this.createExpandableSkillList(
                        matchingSkills,
                        "matching",
                        8
                      ),
                      "matching-skills",
                      true // Open by default
                    )}
                    
                    ${this.createCollapsiblePanel(
                      `<i class="fas fa-times-circle text-danger me-2"></i>Missing Skills (${missingSkills.length})`,
                      this.createExpandableSkillList(
                        missingSkills,
                        "missing",
                        8
                      ),
                      "missing-skills"
                    )}
                    
                    ${
                      recommendations.length > 0
                        ? this.createCollapsiblePanel(
                            `<i class="fas fa-lightbulb text-info me-2"></i>Recommendations (${recommendations.length})`,
                            recommendations.length > 0
                              ? `
                        <ul class="list-unstyled mb-0">
                          ${recommendations
                            .slice(0, 5)
                            .map(
                              (rec, index) => `
                            <li class="mb-2">
                              <i class="fas fa-arrow-right text-muted me-2"></i>
                              ${this.escapeHtml(rec)}
                            </li>
                          `
                            )
                            .join("")}
                          ${
                            recommendations.length > 5
                              ? `
                            <li class="mt-3">
                              <button class="btn btn-sm btn-outline-info" onclick="dashboard.showAllRecommendations('${candidateId}')">
                                <i class="fas fa-plus me-1"></i>View ${
                                  recommendations.length - 5
                                } more recommendations
                              </button>
                            </li>
                          `
                              : ""
                          }
                        </ul>
                      `
                              : '<span class="text-muted">No recommendations available</span>',
                            "recommendations"
                          )
                        : ""
                    }
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
          <div class="col-12">
            <div class="d-flex gap-2 justify-content-end">
              <button class="btn btn-outline-secondary" data-bs-dismiss="modal">
                <i class="fas fa-times me-1"></i>Close
              </button>
              <button class="btn btn-primary" onclick="dashboard.generateDetailedReport('${candidateId}')">
                <i class="fas fa-file-alt me-1"></i>Generate Report
              </button>
            </div>
          </div>
        </div>
      `;

      this.log("Candidate details displayed successfully");

      // Show the modal
      const modal = new bootstrap.Modal(
        document.getElementById("candidate-modal")
      );
      modal.show();
    } catch (error) {
      console.error("Error showing candidate details:", error);
      this.log("Failed to show candidate details:", error.message);
      this.showError("Failed to load candidate details");
    }
  }

  // HTML escape utility method
  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  // Create expandable skill list with show more/less functionality
  createExpandableSkillList(skills, skillType, maxInitialDisplay = 10) {
    if (!skills || skills.length === 0) {
      return `<span class="text-muted">No ${skillType} skills found</span>`;
    }

    const skillsToShow = skills.slice(0, maxInitialDisplay);
    const remainingSkills = skills.slice(maxInitialDisplay);
    const skillClass =
      skillType === "matching" ? "skill-matched" : "skill-missing";
    const expandId = `expand-${skillType}-${Date.now()}`;

    let html = skillsToShow
      .map(
        (skill) =>
          `<span class="skill-tag ${skillClass}">${this.escapeHtml(
            skill
          )}</span>`
      )
      .join("");

    if (remainingSkills.length > 0) {
      html += `
        <div class="skill-expansion" id="${expandId}" style="display: none; margin-top: 0.5rem;">
          ${remainingSkills
            .map(
              (skill) =>
                `<span class="skill-tag ${skillClass}">${this.escapeHtml(
                  skill
                )}</span>`
            )
            .join("")}
        </div>
        <div class="mt-2">
          <button class="btn btn-sm btn-link p-0 text-decoration-none" 
                  onclick="dashboard.toggleSkillExpansion('${expandId}', this)">
            <i class="fas fa-chevron-down me-1"></i>Show ${
              remainingSkills.length
            } more
          </button>
        </div>
      `;
    }

    return html;
  }

  // Toggle skill expansion
  toggleSkillExpansion(expandId, button) {
    const expandDiv = document.getElementById(expandId);
    const icon = button.querySelector("i");
    const isExpanded = expandDiv.style.display !== "none";

    if (isExpanded) {
      expandDiv.style.display = "none";
      icon.className = "fas fa-chevron-down me-1";
      const remainingCount = expandDiv.querySelectorAll(".skill-tag").length;
      button.innerHTML = `<i class="fas fa-chevron-down me-1"></i>Show ${remainingCount} more`;
    } else {
      expandDiv.style.display = "block";
      icon.className = "fas fa-chevron-up me-1";
      button.innerHTML = `<i class="fas fa-chevron-up me-1"></i>Show less`;
    }
  }

  // Create collapsible panel
  createCollapsiblePanel(title, content, id, isOpen = false) {
    const collapseId = `collapse-${id}`;
    const headingId = `heading-${id}`;

    return `
      <div class="accordion-item">
        <h6 class="accordion-header" id="${headingId}">
          <button class="accordion-button ${
            isOpen ? "" : "collapsed"
          }" type="button" 
                  data-bs-toggle="collapse" data-bs-target="#${collapseId}" 
                  aria-expanded="${isOpen}" aria-controls="${collapseId}">
            ${title}
          </button>
        </h6>
        <div id="${collapseId}" class="accordion-collapse collapse ${
      isOpen ? "show" : ""
    }" 
             aria-labelledby="${headingId}">
          <div class="accordion-body">
            ${content}
          </div>
        </div>
      </div>
    `;
  }

  // Create progress bar with tooltip
  createProgressBar(value, label, color = "primary", showTooltip = true) {
    const tooltipAttr = showTooltip
      ? `data-bs-toggle="tooltip" title="${label}: ${value}%"`
      : "";
    return `
      <div class="mb-3">
        <div class="d-flex justify-content-between mb-1">
          <small class="text-muted">${label}</small>
          <small class="fw-bold">${value}%</small>
        </div>
        <div class="progress" style="height: 8px;" ${tooltipAttr}>
          <div class="progress-bar bg-${color}" style="width: ${value}%" role="progressbar"></div>
        </div>
      </div>
    `;
  }

  // Utility methods
  getRelevanceClass(score) {
    if (score >= 70) return "high-relevance";
    if (score >= 40) return "medium-relevance";
    return "low-relevance";
  }

  getScoreClass(score) {
    if (score >= 70) return "score-high";
    if (score >= 40) return "score-medium";
    return "score-low";
  }

  getProgressBarClass(score) {
    if (score >= 70) return "bg-success";
    if (score >= 40) return "bg-warning";
    return "bg-danger";
  }

  getRelevanceBadgeClass(level) {
    switch (level?.toLowerCase()) {
      case "high":
        return "bg-success";
      case "medium":
        return "bg-warning";
      case "low":
        return "bg-danger";
      default:
        return "bg-secondary";
    }
  }

  formatFileSize(bytes) {
    try {
      const numBytes = parseInt(bytes) || 0;
      if (numBytes === 0) return "0 Bytes";
      const k = 1024;
      const sizes = ["Bytes", "KB", "MB", "GB"];
      const i = Math.floor(Math.log(numBytes) / Math.log(k));
      return (
        parseFloat((numBytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
      );
    } catch (error) {
      console.error("Error formatting file size:", error);
      return "Unknown size";
    }
  }

  applyFilters() {
    try {
      this.log("Applying filters");
      this.updateCandidatesTable();
    } catch (error) {
      console.error("Error applying filters:", error);
      this.log("Failed to apply filters:", error.message);
    }
  }

  resetFilters() {
    try {
      this.log("Resetting filters");

      const minScoreFilter = document.getElementById("min-score-filter");
      const skillsFilter = document.getElementById("skills-filter");
      const nameFilter = document.getElementById("name-filter");
      const minScoreValue = document.getElementById("min-score-value");

      if (minScoreFilter) minScoreFilter.value = 0;
      if (skillsFilter) skillsFilter.value = "";
      if (nameFilter) nameFilter.value = "";
      if (minScoreValue) minScoreValue.textContent = "0%";

      this.filters = { minScore: 0, requiredSkills: [], candidateName: "" };
      this.updateCandidatesTable();

      this.log("Filters reset successfully");
    } catch (error) {
      console.error("Error resetting filters:", error);
      this.log("Failed to reset filters:", error.message);
    }
  }

  sortCandidates() {
    try {
      this.log("Sorting candidates");
      this.updateCandidatesTable();
    } catch (error) {
      console.error("Error sorting candidates:", error);
      this.log("Failed to sort candidates:", error.message);
    }
  }

  compareCandidate(candidateId) {
    try {
      this.log("Compare candidate:", candidateId);
      // Implementation for candidate comparison
      console.log("Compare candidate:", candidateId);
    } catch (error) {
      console.error("Error comparing candidate:", error);
      this.log("Failed to compare candidate:", error.message);
    }
  }

  clearResults() {
    try {
      this.log("Clearing all results and resetting UI");

      this.analysisResults = [];
      this.jobFile = null;
      this.resumeFiles = [];

      // Reset UI
      const resultsContainer = document.getElementById("results-container");
      if (resultsContainer) {
        resultsContainer.innerHTML = `
          <div class="text-center text-muted py-5">
              <i class="fas fa-chart-bar fa-3x mb-3"></i>
              <p class="lead">Upload files and click "Analyze Resumes" to see results</p>
          </div>
        `;
      }

      this.updateCandidatesTable();
      this.updateAnalyzeButton();

      // Reset upload areas
      ["job-upload-area", "resume-upload-area"].forEach((areaId) => {
        const area = document.getElementById(areaId);
        if (area) {
          area.classList.remove("success", "error");
        }
      });

      ["job-status", "resume-status"].forEach((statusId) => {
        const statusElement = document.getElementById(statusId);
        if (statusElement) {
          statusElement.innerHTML = "";
        }
      });

      // Reset charts
      Object.values(this.charts).forEach((chart) => {
        try {
          if (chart && chart.data && chart.data.datasets) {
            chart.data.datasets.forEach((dataset) => {
              if (Array.isArray(dataset.data)) {
                dataset.data.fill(0);
              }
            });
            if (chart.data.labels && Array.isArray(chart.data.labels)) {
              chart.data.labels.length = 0;
            }
            chart.update();
          }
        } catch (chartError) {
          console.error("Error resetting chart:", chartError);
        }
      });

      this.log("Results cleared successfully");
    } catch (error) {
      console.error("Error clearing results:", error);
      this.log("Failed to clear results:", error.message);
    }
  }

  exportResults() {
    try {
      if (this.analysisResults.length === 0) {
        this.showError("No results to export");
        return;
      }

      this.log("Exporting results to JSON");

      const exportData = {
        timestamp: new Date().toISOString(),
        jobDescription: this.jobFile?.filename || "Unknown",
        totalCandidates: this.analysisResults.length,
        results: this.analysisResults.map((result) => ({
          candidate: result.candidate?.filename || "Unknown",
          relevanceScore: result.relevance_score || 0,
          skillMatchPercentage: result.skill_match_percentage || 0,
          relevanceLevel: result.relevance_level || "Unknown",
          matchingSkills: result.matching_skills || [],
          missingSkills: result.missing_skills || [],
          recommendations: result.recommendations || [],
        })),
      };

      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: "application/json",
      });

      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `resume-analysis-${
        new Date().toISOString().split("T")[0]
      }.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      this.log("Results exported successfully");
    } catch (error) {
      console.error("Error exporting results:", error);
      this.log("Failed to export results:", error.message);
      this.showError("Failed to export results");
    }
  }

  showLoading(show, message = "Processing...") {
    try {
      let overlay = document.getElementById("loading-overlay");

      if (show) {
        if (!overlay) {
          // Create loading overlay if it doesn't exist
          overlay = document.createElement("div");
          overlay.id = "loading-overlay";
          overlay.className = "loading-overlay";
          overlay.innerHTML = `
            <div class="loading-content">
              <div class="loading-spinner-large"></div>
              <h5 id="loading-message">${message}</h5>
              <p class="text-muted">Please wait...</p>
            </div>
          `;
          document.body.appendChild(overlay);
        } else {
          const messageEl = document.getElementById("loading-message");
          if (messageEl) messageEl.textContent = message;
        }
        overlay.style.display = "flex";
      } else {
        if (overlay) {
          overlay.style.display = "none";
        }
      }

      this.log(`Loading overlay ${show ? "shown" : "hidden"}`);
    } catch (error) {
      console.error("Error controlling loading overlay:", error);
      this.log("Failed to control loading overlay:", error.message);
    }
  }

  showSuccess(message, duration = 4000) {
    this.showNotification(message, "success", duration);
  }

  showNotification(message, type = "info", duration = 4000) {
    try {
      const notification = document.createElement("div");
      notification.className = `notification notification-${type}`;
      notification.innerHTML = `
        <div class="d-flex align-items-center">
          <i class="fas fa-${
            type === "success" ? "check-circle" : "exclamation-circle"
          } me-2"></i>
          <span>${message}</span>
          <button class="btn btn-sm btn-link text-white ms-auto" onclick="this.parentElement.parentElement.remove()">
            <i class="fas fa-times"></i>
          </button>
        </div>
      `;

      document.body.appendChild(notification);

      // Auto-remove after duration
      setTimeout(() => {
        if (notification.parentElement) {
          notification.remove();
        }
      }, duration);

      this.log(`${type} notification shown: ${message}`);
    } catch (error) {
      console.error("Error showing notification:", error);
      // Fallback to alert
      alert(`${type.toUpperCase()}: ${message}`);
    }
  }

  showError(message) {
    try {
      console.error("Error:", message);
      this.log("Error displayed to user:", message);

      // Try to create a proper toast notification
      if (typeof bootstrap !== "undefined" && bootstrap.Toast) {
        const toast = document.createElement("div");
        toast.className = "toast position-fixed top-0 end-0 m-3";
        toast.setAttribute("role", "alert");
        toast.setAttribute("style", "z-index: 9999;");
        toast.innerHTML = `
          <div class="toast-header bg-danger text-white">
            <i class="fas fa-exclamation-triangle me-2"></i>
            <strong class="me-auto">Error</strong>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
          </div>
          <div class="toast-body">
            ${this.escapeHtml(message)}
          </div>
        `;

        document.body.appendChild(toast);
        const bootstrapToast = new bootstrap.Toast(toast);
        bootstrapToast.show();

        // Clean up after toast is hidden
        toast.addEventListener("hidden.bs.toast", () => {
          try {
            document.body.removeChild(toast);
          } catch (e) {
            // Toast already removed
          }
        });
      } else {
        // Fallback to alert if Bootstrap toast not available
        alert(message);
      }
    } catch (error) {
      console.error("Error showing error message:", error);
      // Final fallback to alert
      alert(message);
    }
  }

  async checkSystemHealth() {
    try {
      this.log("Checking system health");

      const response = await fetch("/health", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const indicator = document.getElementById("system-status");

      if (!indicator) {
        this.log("Warning: System status indicator not found");
        return;
      }

      if (response.ok) {
        const status = await response.json();

        if (status.status === "healthy") {
          indicator.className = "badge bg-success";
          indicator.textContent = "System Online";
          this.log("System health check: Healthy");
        } else {
          indicator.className = "badge bg-warning";
          indicator.textContent = "System Issues";
          this.log("System health check: Issues detected", status);
        }
      } else {
        indicator.className = "badge bg-danger";
        indicator.textContent = "System Offline";
        this.log("System health check: Server error", response.status);
      }
    } catch (error) {
      console.error("System health check failed:", error);
      this.log("System health check failed:", error.message);

      const indicator = document.getElementById("system-status");
      if (indicator) {
        indicator.className = "badge bg-danger";
        indicator.textContent = "System Offline";
      }
    }
  }

  /**
   * Get progress bar color class based on score
   */
  getProgressBarColorClass(score) {
    if (score >= 80) return "success";
    if (score >= 60) return "warning";
    if (score >= 40) return "info";
    return "danger";
  }

  /**
   * Show all recommendations for a candidate
   */
  showAllRecommendations(candidateId) {
    // Find the candidate data
    const candidate = this.allCandidates.find((c) => c.id === candidateId);
    if (!candidate) return;

    const { recommendations = [] } = candidate;

    const modal = new bootstrap.Modal(
      document.getElementById("allRecommendationsModal") ||
        this.createAllRecommendationsModal()
    );

    const modalBody = modal._element.querySelector(".modal-body");
    modalBody.innerHTML = `
      <div class="list-group">
        ${recommendations
          .map(
            (rec, index) => `
          <div class="list-group-item">
            <div class="d-flex align-items-start">
              <span class="badge bg-primary me-3">${index + 1}</span>
              <span>${this.escapeHtml(rec)}</span>
            </div>
          </div>
        `
          )
          .join("")}
      </div>
    `;

    modal.show();
  }

  /**
   * Create all recommendations modal if it doesn't exist
   */
  createAllRecommendationsModal() {
    const modalHtml = `
      <div class="modal fade" id="allRecommendationsModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">
                <i class="fas fa-lightbulb text-warning me-2"></i>All Recommendations
              </h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <!-- Content will be populated dynamically -->
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
          </div>
        </div>
      </div>
    `;

    document.body.insertAdjacentHTML("beforeend", modalHtml);
    return document.getElementById("allRecommendationsModal");
  }

  /**
   * Generate detailed report for candidate
   */
  generateDetailedReport(candidateId) {
    // Find the candidate data
    const candidate = this.allCandidates.find((c) => c.id === candidateId);
    if (!candidate) return;

    // Show loading state
    const button = event.target;
    const originalText = button.innerHTML;
    button.innerHTML =
      '<i class="fas fa-spinner fa-spin me-1"></i>Generating...';
    button.disabled = true;

    // Simulate report generation (replace with actual API call)
    setTimeout(() => {
      this.downloadCandidateReport(candidate);

      // Reset button
      button.innerHTML = originalText;
      button.disabled = false;
    }, 2000);
  }

  /**
   * Download candidate report as text file
   */
  downloadCandidateReport(candidate) {
    const {
      filename,
      relevanceScore,
      skillMatchPercentage,
      matchingSkills,
      missingSkills,
      recommendations,
      relevanceLevel,
    } = candidate;

    const reportContent = `
CANDIDATE ANALYSIS REPORT
========================

Candidate: ${filename}
Analysis Date: ${new Date().toLocaleString()}
Relevance Level: ${relevanceLevel}

SCORES & METRICS
================
Overall Relevance Score: ${relevanceScore.toFixed(1)}%
Skill Match Percentage: ${skillMatchPercentage.toFixed(1)}%

MATCHING SKILLS (${matchingSkills.length})
${
  matchingSkills.length > 0
    ? "================\\n" +
      matchingSkills.map((skill) => `• ${skill}`).join("\\n")
    : "================\\nNo matching skills found"
}

MISSING SKILLS (${missingSkills.length})
${
  missingSkills.length > 0
    ? "==============\\n" +
      missingSkills.map((skill) => `• ${skill}`).join("\\n")
    : "==============\\nNo missing skills identified"
}

RECOMMENDATIONS (${recommendations.length})
${
  recommendations.length > 0
    ? "===============\\n" +
      recommendations.map((rec, i) => `${i + 1}. ${rec}`).join("\\n")
    : "===============\\nNo recommendations available"
}

---
Generated by Resume Relevance System
    `.trim();

    // Create and download file
    const blob = new Blob([reportContent], { type: "text/plain" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${filename.replace(/\\.[^/.]+$/, "")}_analysis_report.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);

    // Show success message
    this.showToast("Report downloaded successfully!", "success");
  }
}

// Initialize dashboard when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  window.dashboard = new ResumeDashboard();
});
