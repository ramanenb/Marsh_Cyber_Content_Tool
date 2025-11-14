/**
=========================================================================
* Data Repository Page 
=========================================================================
*/

// Material Dashboard 2 React components
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import IconButton from "@mui/material/IconButton";
import DeleteIcon from "@mui/icons-material/Delete";
import MDButton from "components/MDButton";
import CircularProgress from "@mui/material/CircularProgress";
import Snackbar from "@mui/material/Snackbar";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogActions from "@mui/material/DialogActions";
import MuiAlert from "@mui/material/Alert";

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import DataTable from "examples/Tables/DataTable";
import { useEffect } from "react";
import { fetchWithFallback } from "utils/apiConfig";

// state
import { useState, useCallback } from "react";
function Repo() {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [loadingFetch, setLoadingFetch] = useState(false);
  const [successFetch, setSuccessFetch] = useState(false);
  const [mongoData, setMongoData] = useState([]);
  const [uploadedFileLinks, setUploadedFileLinks] = useState([]);
  const [uploadedPptxLinks, setUploadedPptxLinks] = useState([]);
  const [duplicates, setDuplicates] = useState([]);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [pendingUploadData, setPendingUploadData] = useState(null);

  //mongo Data
  const fetchMongoData = async () => {
    try {
      const res = await fetchWithFallback("/api/get_prop_data/");
      const result = await res.json();
      console.log("Sample record from API:", result.data?.[0]);

      if (result.status === "success") {
        setMongoData(result.data);
      } else {
        console.error("Error fetching MongoDB data:", result.message);
      }
    } catch (err) {
      console.error("Failed to fetch MongoDB data:", err);
    }
  };

  // s3 file links
  const fetchUploadedFiles = async () => {
    try {
      const res = await fetchWithFallback("/api/list_uploaded_files/");
      const result = await res.json();

      if (result.status === "success") {
        setUploadedFileLinks(result.data);
      } else {
        console.error("Error fetching uploaded files:", result.message);
      }
    } catch (err) {
      console.error("Failed to fetch uploaded files:", err);
    }
  };

  // pptx file links
  const fetchUploadedPptxFiles = async () => {
    try {
      const res = await fetchWithFallback("/api/ppt/list_s3_ppt/");
      const result = await res.json();
      console.log("Fetched PPTX result:", result);

      if (result.status === "success") {
        setUploadedPptxLinks(result.data);
      } else {
        console.error("Error fetching uploaded pptx files:", result.message);
      }
    } catch (err) {
      console.error("Failed to fetch uploaded pptx files:", err);
    }
  };

  useEffect(() => {
    fetchMongoData();
    fetchUploadedFiles();
    fetchUploadedPptxFiles();
  }, []);

  // Handle dropped files
  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = Array.from(e.dataTransfer.files);
    setUploadedFiles((prev) => [...prev, ...files]);
  }, []);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleUpload = async () => {
    if (uploadedFiles.length === 0) return;

    const file = uploadedFiles[0];
    const formData = new FormData();
    formData.append("file", file);

    try {
      // Check for duplicates
      const checkRes = await fetchWithFallback("/api/check_duplicates/", {
        method: "POST",
        body: formData,
      });

      const checkData = await checkRes.json();

      if (checkData.status === "success" && checkData.duplicates.length > 0) {
        setDuplicates(checkData.duplicates);
        setPendingUploadData(formData);
        setConfirmOpen(true);
        setSnackbar({
          open: true,
          message: `Duplicate detected: ${checkData.duplicates.length} existing claim(s) found.`,
          color: "warning", // yellow alert
        });
        return;
      }

      // No duplicates go straight to upload
      await performUpload(formData);
      
    } catch (err) {
      console.error("Error checking duplicates:", err);
    }
  };

  const performUpload = async (formData) => {
    setLoading(true);
    setSuccess(false);

    try {
      const res = await fetchWithFallback("/api/upload_prop_data/", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      console.log("Upload response:", data);

      if (data.status === "success") {
        setSnackbar({
          open: true,
          message: "Uploaded successfully!",
          color: "success",
        });
        setSuccess(true); // indicate success
        setUploadedFiles([]); // clear uploaded files
        await fetchMongoData(); // refresh data from MongoDB
        await fetchUploadedFiles(); // refresh uploaded files list
      } else {
        console.error("Upload failed:", data);
        setSuccess(false);
      }
    } catch (err) {
      console.error("Upload failed:", err);
      //setSuccess(false);
    } finally {
      setLoading(false); // stop loading
      setConfirmOpen(false);
    }
  };
  // placeholder fetch handler
  const handleFakeFetch = () => {
    setLoadingFetch(true);
    setSuccessFetch(false);
    setSnackbar({ open: false, message: "", color: "info" });

    // Simulate a 3-second fetch delay
    setTimeout(() => {
      setLoadingFetch(false);
      setSuccessFetch(true);
      setSnackbar({
        open: true,
        message: "Data fetched successfully!",
        color: "success",
      });
    }, 5000);
  };

  // snackbar feedback
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    color: "info",
  });

  useEffect(() => {
    if (snackbar.open) {
      const timer = setTimeout(() => {
        setSnackbar((prev) => ({ ...prev, open: false }));
      }, 3000); // 3 seconds

      return () => clearTimeout(timer); // cleanup if unmounted or snackbar closes early
    }
  }, [snackbar.open]);

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox px={3} pt={3}>
        <MDTypography variant="h6">
          Upload Proprietary Data (Optional)
        </MDTypography>

        <MDBox display="flex" flexDirection="column" gap={2} mt={1}>
          <MDTypography variant="body2" color="text">
            You can upload multiple files (xlsx, PDF, etc.)
          </MDTypography>

          {/* Drag-and-Drop Zone */}
          <MDBox
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            border="2px dashed"
            borderColor={dragActive ? "info.main" : "grey.400"}
            borderRadius="lg"
            p={4}
            textAlign="center"
            sx={{
              transition: "border-color 0.2s ease",
              cursor: "pointer",
            }}
          >
            <MDTypography variant="body2" color="text">
              {dragActive ? "Drop files here..." : "Drag & Drop files here"}
            </MDTypography>
            <MDButton
              color="info"
              variant="outlined"
              size="small"
              component="label"
              sx={{ mt: 1 }}
            >
              Browse Files
              <input
                type="file"
                hidden
                multiple
                onChange={(e) => {
                  const files = Array.from(e.target.files);
                  setUploadedFiles((prev) => [...prev, ...files]);
                }}
              />
            </MDButton>
          </MDBox>

          {/* Show Uploaded Files */}
          {uploadedFiles && uploadedFiles.length > 0 && (
            <MDBox mt={2}>
              <MDTypography variant="subtitle2">Uploaded Files:</MDTypography>
              <ul style={{ marginTop: 4, paddingLeft: 20 }}>
                {uploadedFiles.map((file, idx) => (
                  <li
                    key={idx}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      maxWidth: 300,
                    }}
                  >
                    <MDTypography variant="body2">{file.name}</MDTypography>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() =>
                        setUploadedFiles((prev) =>
                          prev.filter((_, i) => i !== idx)
                        )
                      }
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </li>
                ))}
              </ul>
            </MDBox>
          )}
        </MDBox>

        <MDBox mt={2}>
          {uploadedFiles.length > 0 && (
            <MDButton onClick={handleUpload} color="info" disabled={loading}>
              {loading && (
                <CircularProgress size={18} color="inherit" sx={{ mr: 1 }} />
              )}
              {loading ? "Uploading..." : "Process & Upload"}
            </MDButton>
          )}

          {success && (
            <MDTypography variant="body2" color="success.main" mt={1}>
              Upload successful!
            </MDTypography>
          )}
        </MDBox>
        <MDBox mt={6} textAlign="center">
          <MDTypography variant="h6">
            Manually Fetch Latest Data (Optional)
          </MDTypography>
          <MDTypography variant="body2" color="text" mb={2}>
            Click below to fetch the latest records from the database.
          </MDTypography>
          <MDBox mt={2}>
            <MDButton onClick={handleFakeFetch} color="info" disabled={loadingFetch}>
              {loadingFetch && (
                <CircularProgress size={18} color="inherit" sx={{ mr: 1 }} />
              )}
              {loadingFetch ? "Fetching..." : "Fetch Data"}
            </MDButton>

            {successFetch && (
              <MDTypography variant="body2" color="success.main" mt={1}>
                Data is displayed in the MongoDB Records Table below.
              </MDTypography>
            )}
          </MDBox>
        </MDBox>
        {mongoData.length > 0 && (
          <MDBox mt={4} pt={3}>
            <Grid container spacing={6}>
              <Grid item xs={12}>
                <Card>
                  <MDBox
                    mx={2}
                    mt={-3}
                    py={3}
                    px={2}
                    variant="gradient"
                    bgColor="info"
                    borderRadius="lg"
                    coloredShadow="info"
                  >
                    <MDTypography variant="h6" color="white">
                      MongoDB Records
                    </MDTypography>
                  </MDBox>
                  <DataTable
                    table={{
                      columns: [
                        { Header: "Claim Number", accessor: "_id" },
                        { Header: "Client Name", accessor: "Client Name" },
                        { Header: "Coverage", accessor: "Coverage" },
                        { Header: "Incident Date", accessor: "Incident Date" },
                        { Header: "Country", accessor: "Country (Set ID)" },
                        { Header: "Cause", accessor: "Cause" },
                        { Header: "Type of Claim", accessor: "Type of Claim" },
                        { Header: "Industry", accessor: "Industry" },
                        {
                          Header: "Total Paid (USD)",
                          accessor: "Total Paid (USD)",
                          Cell: ({ value }) =>
                            value !== undefined && value !== null
                              ? value.toLocaleString("en-US", {
                                  minimumFractionDigits: 2,
                                  maximumFractionDigits: 2,
                                })
                              : "-",
                        },
                        { Header: "Claim Result", accessor: "Claim Result" },
                      ],
                      rows: mongoData.map((item) => {
                        // console.log("Parsing date:", item["Incident Date"]);
                        const parsed = new Date(item["Incident Date"]);
                        // console.log("Parsed result:", parsed);
                        return {
                          ...item,
                          "Incident Date": item["Incident Date"]
                            ? parsed.toLocaleDateString()
                            : "N/A",
                        };
                      }),
                    }}
                    isSorted={true}
                    entriesPerPage={{
                      defaultValue: 8,
                      entries: [8, 15, 25, 50],
                    }}
                    showTotalEntries={false}
                    canSearch={true}
                    noEndBorder
                  />
                </Card>
              </Grid>
            </Grid>
          </MDBox>
        )}

        {uploadedFileLinks.length > 0 && (
          <MDBox mt={6}>
            <Grid container spacing={6}>
              <Grid item xs={12}>
                <Card>
                  <MDBox
                    mx={2}
                    mt={-3}
                    py={3}
                    px={2}
                    variant="gradient"
                    bgColor="info"
                    borderRadius="lg"
                    coloredShadow="info"
                  >
                    <MDTypography variant="h6" color="white">
                      Uploaded Proprietary Data Files
                    </MDTypography>
                  </MDBox>

                  <DataTable
                    table={{
                      columns: [
                        { Header: "File Name", accessor: "filename" },
                        {
                          Header: "Uploaded At",
                          accessor: "uploaded_at",
                          Cell: ({ value }) =>
                            value
                              ? new Date(value).toLocaleString()
                              : "Unknown",
                        },
                        {
                          Header: "Download Link",
                          accessor: "url",
                          Cell: ({ value }) => (
                            <MDButton
                              color="info"
                              size="small"
                              component="a"
                              href={value}
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              Open
                            </MDButton>
                          ),
                        },
                      ],
                      rows: uploadedFileLinks,
                    }}
                    isSorted={false}
                    entriesPerPage={{ defaultValue: 5, entries: [5, 10, 20] }}
                    showTotalEntries={false}
                    noEndBorder
                  />
                </Card>
              </Grid>
            </Grid>
          </MDBox>
        )}

        {uploadedPptxLinks.length > 0 && (
          <MDBox mt={6}>
            <Grid container spacing={6}>
              <Grid item xs={12}>
                <Card>
                  <MDBox
                    mx={2}
                    mt={-3}
                    py={3}
                    px={2}
                    variant="gradient"
                    bgColor="info"
                    borderRadius="lg"
                    coloredShadow="info"
                  >
                    <MDTypography variant="h6" color="white">
                      Generated PPTX Files
                    </MDTypography>
                  </MDBox>

                  <DataTable
                    table={{
                      columns: [
                        { Header: "File Name", accessor: "filename" },
                        {
                          Header: "Uploaded At",
                          accessor: "uploaded_at",
                          Cell: ({ value }) =>
                            value
                              ? new Date(value).toLocaleString()
                              : "Unknown",
                        },
                        {
                          Header: "Download Link",
                          accessor: "url",
                          Cell: ({ value }) => (
                            <MDButton
                              color="info"
                              size="small"
                              component="a"
                              href={value}
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              Open
                            </MDButton>
                          ),
                        },
                      ],
                      rows: uploadedPptxLinks,
                    }}
                    isSorted={false}
                    entriesPerPage={{ defaultValue: 5, entries: [5, 10, 20] }}
                    showTotalEntries={false}
                    noEndBorder
                  />
                </Card>
              </Grid>
            </Grid>
          </MDBox>
        )}
      </MDBox>

      <Dialog
        open={confirmOpen}
        onClose={() => setConfirmOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Duplicate Claims Found</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Some claim numbers already exist in the database:
            <br />
            <br />
            {duplicates.slice(0, 5).join(", ")}
            {duplicates.length > 5 && "..."}
            <br />
            <br />
            Do you want to overwrite them? This will replace any existing data
            for those claims.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <MDButton onClick={() => setConfirmOpen(false)}>Cancel</MDButton>
          <MDButton
            onClick={async () => {
              setConfirmOpen(false);
              await performUpload(pendingUploadData);
            }}
            color="error"
            variant="contained"
          >
            Overwrite & Upload
          </MDButton>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={8000} // disappears after 3 seconds
        anchorOrigin={{ vertical: "top", horizontal: "right" }} // top center
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <MuiAlert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.color} // 'success', 'error', 'info', 'warning'
          variant="filled"
          sx={{ width: "100%" }}
        >
          {snackbar.message}
        </MuiAlert>
      </Snackbar>
    </DashboardLayout>
  );
}

export default Repo;
