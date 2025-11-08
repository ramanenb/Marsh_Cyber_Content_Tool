/**
=========================================================
* Material Dashboard 2 React - v2.2.0
=========================================================
*/

// @mui material components
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import DialogContentText from '@mui/material/DialogContentText';
import Button from "@mui/material/Button";
import MenuItem from "@mui/material/MenuItem";
import IconButton from "@mui/material/IconButton";
import DeleteIcon from "@mui/icons-material/Delete";
import Checkbox from "@mui/material/Checkbox";
import CircularProgress from "@mui/material/CircularProgress";
import Snackbar from "@mui/material/Snackbar";
import MuiAlert from "@mui/material/Alert";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import DataTable from "examples/Tables/DataTable";

// state/hooks
import { useState, useEffect, useMemo } from "react";
import { fetchWithFallback } from "utils/apiConfig";

function Slides() {
  // proprietary data
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [duplicates, setDuplicates] = useState([]);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [pendingUploadData, setPendingUploadData] = useState(null);

  // Handle dropped files
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

      if (data.status == "success") {
        setSnackbar({
          open: true,
          message: "Uploaded successfully!",
          color: "success",
        });
        setSuccess(true); // indicate success
        setUploadedFiles([]); // clear uploaded files
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

  // industries data
  const [industryOptions, setIndustryOptions] = useState([]);
  const [selectedIndustries, setSelectedIndustries] = useState([]);
  useEffect(() => {
    const fetchIndustries = async () => {
      try {
        const response = await fetchWithFallback("/api/getIndustries");
        const data = await response.json();
        if (data.industries) setIndustryOptions(data.industries);
      } catch (error) {
        console.error("Failed to fetch industries:", error);
      }
    };
    fetchIndustries();
  }, []);
  //industry functions

  const handleDeleteIndustry = (index) => {
    const updated = [...selectedIndustries];
    updated.splice(index, 1);
    setSelectedIndustries(updated);
  };

  //region data
  const [newRegion, setNewRegion] = useState("");
  const [regionOptions] = useState([
    "Africa",
    "Asia",
    "Europe",
    "North America",
    "Oceania",
    "South America",
  ]);

  //date data
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  //client context data
  const [clientContext, setClientContext] = useState("");

  //incident data
  const [incidentsData, setIncidentsData] = useState([]);
  const [incidentColumns] = useState([
    { Header: "", accessor: "select", width: "5%", align: "center" },
    {
      Header: "Date",
      accessor: "date",
      width: "15%",
      Cell: ({ value }) => {
        if (!value || value === "NA") return "—";
        const date = new Date(value);
        return date.toLocaleDateString("en-US", {
          year: "numeric",
          month: "short",
          day: "numeric",
        });
      },
    },

    { Header: "company", accessor: "company", width: "15%", align: "left" },
    {
      Header: "Incident Details",
      accessor: "executive_summary",
      align: "left",
    },
    {
      Header: "hallucination",
      accessor: "hallucination_classification",
      align: "center",
    },
    {
      Header: "summariser",
      accessor: "summariser_classification",
      align: "center",
    },
    { Header: "action", accessor: "action", align: "center" },
  ]);
  const [showIncidents, setShowIncidents] = useState(false);

  // store indices of selected incidents
  const [selectedIncidents, setSelectedIncidents] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [selectedFunction, setSelectedFunction] = useState("");
  // incident functions
  const handleGetIncidents = async () => {
    setLoadingIncidents(true);
    try {
      const response = await fetchWithFallback("/api/getIncidents", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: clientContext
            ? `cyber incidents: ${clientContext}`
            : "cyber incidents",
          industries: selectedIndustries.length > 0 ? selectedIndustries : [],
          region: newRegion || null,
          startDate: startDate || null,
          endDate: endDate || null,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`);
      }

      const data = await response.json();

      // `data.evaluated_articles` is the list you need to show in your table
      if (data && data.evaluated_articles) {
        // Sort incidents by date (newest first)
        const sortedArticles = [...data.evaluated_articles].sort((a, b) => {
          const dateA = new Date(a.date || 0);
          const dateB = new Date(b.date || 0);
          return dateB - dateA; // descending order
        });
        const filtered = sortedArticles.filter((item) => {
          const itemDate = new Date(item.date);
          if (startDate && itemDate < new Date(startDate)) return false;
          if (endDate && itemDate > new Date(endDate)) return false;
          return true;
        });

        setIncidentsData(filtered);
        setShowIncidents(true);
        setSelectedIncidents([]);
      } else {
        console.warn("No evaluated articles returned:", data);
        setIncidentsData([]);
      }
    } catch (error) {
      console.error("Failed to fetch incidents:", error);
    } finally {
      setLoadingIncidents(false);
    }
  };

  const truncateText = (text, wordLimit = 5) => {
    if (!text) return "—";
    const words = text.split(" ");
    return words.length > wordLimit
      ? words.slice(0, wordLimit).join(" ") + "..."
      : text;
  };

  // table function
  const tableRows = useMemo(() => {
    return incidentsData.map((item, index) => ({
      select: (
        <Checkbox
          size="small"
          checked={selectedIncidents.includes(index)}
          onChange={(e) => {
            setSelectedIncidents((prev) =>
              e.target.checked
                ? [...prev, index]
                : prev.filter((i) => i !== index)
            );
          }}
        />
      ),
      date: item.date, // add date field for the Date column
      company: item.affected_organization || "N/A",
      executive_summary: truncateText(item.executive_summary, 5),
      hallucination_classification:
        item.hallucination_classification || "unknown",
      summariser_classification: item.summariser_classification || "unknown",
      action: (
        <MDButton
          variant="outlined"
          color="info"
          size="small"
          onClick={() => {
            setSelectedFunction({
              company: item.company || "",
              executive_summary: item.executive_summary || "",
              background: item.background || "",
              malicious_activity: item.malicious_activity || "",
              outcomes_and_losses: item.outcomes_and_losses || "",
              source_url: item.source_url || "",
              hallucination_explanation: item.hallucination_explanation || "",
              summariser_explanation: item.summariser_explanation || "",
            });
            setIsEditing(false);
            setOpenDialog(true);
          }}
        >
          View
        </MDButton>
      ),
    }));
  }, [incidentsData, selectedIncidents]);

  // loading
  const [loadingIncidents, setLoadingIncidents] = useState(false);
  const [loadingExport, setLoadingExport] = useState(false);

  // export function
  const handleExportPowerPoint = async () => {
    if (selectedIncidents.length === 0) {
      setSnackbar({
        open: true,
        message: "Please select at least one incident before exporting.",
        color: "error",
      });
      return;
    }

    setLoadingExport(true);

    try {
      const shortlisted = selectedIncidents.map((i) => {
        const item = incidentsData[i];
        return {
          source: item.source || "Unknown Source",
          executive_summary: item.executive_summary || "",
          background: item.background || "",
          malicious_activity: item.malicious_activity || "",
          outcomes_and_losses: item.outcomes_and_losses || "",
          reference_text: item.reference_text || "",
          summarised_text: item.summarised_text || "",
          source_url: item.source_url || "",
          affected_organization: item.affected_organization || "",
          hallucination_classification:
            item.hallucination_classification || "N/A",
          hallucination_explanation: item.hallucination_explanation || "",
          summarizer_classification: item.summariser_classification || "N/A",
          summarizer_explanation: item.summariser_explanation || "",
        };
      });

      const payload = {
        query: clientContext
          ? `cyber incidents: ${clientContext}`
          : "cyber incidents",
        industries: selectedIndustries.length > 0 ? selectedIndustries : [],
        region: newRegion || null,
        shortlisted_articles: shortlisted,
      };

      const response = await fetchWithFallback(
        "/api/ppt/generate-presentation",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok)
        throw new Error(`Server responded with status ${response.status}`);

      const result = await response.json();
      console.log("PowerPoint export result:", result);

      if (result.success && result.download_url) {
        window.open(result.download_url, "_blank");
        setSnackbar({
          open: true,
          message: "Presentation generated successfully!",
          color: "success",
        });
      } else {
        setSnackbar({
          open: true,
          message: "Failed to generate PowerPoint. Please check the logs.",
          color: "error",
        });
      }
    } catch (error) {
      console.error("Export failed:", error);
      setSnackbar({
        open: true,
        message: "Error exporting PowerPoint: " + error.message,
        color: "error",
      });
    } finally {
      setLoadingExport(false);
    }
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

          <MDButton
            color="info"
            variant="outlined"
            size="small"
            component="label"
            sx={{ alignSelf: "flex-start" }}
          >
            Browse Files
            <input
              type="file"
              hidden
              multiple
              onChange={(e) => {
                const uploaded = Array.from(e.target.files);
                setUploadedFiles((prev) => [...prev, ...uploaded]);
              }}
            />
          </MDButton>

          {uploadedFiles && uploadedFiles.length > 0 && (
            <MDBox mt={1}>
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
      </MDBox>

      <MDBox px={3} pt={3}>
          {uploadedFiles.length > 0 && (
            <MDButton onClick={handleUpload} color="info" disabled={loading}>
              {loading && <CircularProgress size={18} color="inherit" sx={{ mr: 1 }} />}
              {loading ? "Uploading..." : "Process & Upload"}
            </MDButton>
          )}

          {success && (
            <MDTypography variant="body2" color="success.main" mt={1}>
              Upload successful!
            </MDTypography>
          )}
      </MDBox>
      
      <Dialog
        open={confirmOpen}
        onClose={() => setConfirmOpen(false)}
        maxWidth="sm"
        fullWidth>
        <DialogTitle>Duplicate Claims Found</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Some claim numbers already exist in the database:
            <br /><br />
            {duplicates.slice(0, 5).join(", ")}
            {duplicates.length > 5 && "..."}
            <br /><br />
            Do you want to overwrite them? This will replace any existing data for those claims.
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
            variant="contained">
            Overwrite & Upload
          </MDButton>
        </DialogActions>
      </Dialog>

      <MDBox px={3} pt={3}>
        <MDTypography variant="h6">Select Industries</MDTypography>

        <MDBox display="flex" gap={1} flexWrap="wrap">
          {selectedIndustries.map((industry, index) => (
            <MDBox
              key={index}
              display="flex"
              alignItems="center"
              px={1.5}
              py={0.5}
              borderRadius="md"
              bgcolor="grey.200"
            >
              <MDTypography variant="body2">{industry}</MDTypography>
              <IconButton
                size="small"
                color="error"
                onClick={() => handleDeleteIndustry(index)}
              >
                <DeleteIcon fontSize="small" />
              </IconButton>
            </MDBox>
          ))}
        </MDBox>

        <MDBox display="flex" mt={1} gap={1} alignItems="center">
          <MDInput
            select
            label="Select Industry"
            value=""
            onChange={(e) => {
              const selected = e.target.value;
              if (!selectedIndustries.includes(selected)) {
                setSelectedIndustries([...selectedIndustries, selected]);
              }
            }}
            sx={{ minWidth: 300 }}
            InputProps={{
              style: { minHeight: 50, padding: "12px" },
            }}
          >
            {industryOptions.map((option) => (
              <MenuItem key={option} value={option}>
                {option}
              </MenuItem>
            ))}
          </MDInput>
        </MDBox>
      </MDBox>

      <MDBox px={3} pt={3}>
        <MDTypography variant="h6">Select Region</MDTypography>
        <MDBox display="flex" gap={1} mt={1}>
          <MDInput
            select
            label="Add Region"
            variant="outlined"
            fullWidth
            value={newRegion}
            onChange={(e) => setNewRegion(e.target.value)}
            sx={{ minWidth: 300 }}
            InputProps={{
              style: { minHeight: 50, padding: "12px" },
            }}
          >
            {regionOptions.map((option) => (
              <MenuItem key={option} value={option}>
                {option}
              </MenuItem>
            ))}
          </MDInput>
        </MDBox>
      </MDBox>
      <MDBox px={3} pt={3}>
        <MDTypography variant="h6">Select Date Range (Optional)</MDTypography>
        <MDBox display="flex" gap={2} mt={1}>
          <MDInput
            type="date"
            label="Start Date"
            variant="outlined"
            fullWidth
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            InputLabelProps={{ shrink: true }}
            sx={{ minWidth: 250 }}
          />
          <MDInput
            type="date"
            label="End Date"
            variant="outlined"
            fullWidth
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            InputLabelProps={{ shrink: true }}
            sx={{ minWidth: 250 }}
          />
        </MDBox>
      </MDBox>

      <MDBox px={3} pt={3}>
        <MDTypography variant="h6">Provide Client Context</MDTypography>
        <MDBox display="flex" gap={1} mt={1}>
          <MDInput
            label="Client Context"
            variant="outlined"
            fullWidth
            value={clientContext}
            onChange={(e) => setClientContext(e.target.value)}
          />
        </MDBox>
      </MDBox>

      <MDBox px={3} pt={3}>
        <MDButton
          color="info"
          variant="outlined"
          onClick={handleGetIncidents}
          disabled={loadingIncidents}
          sx={{ display: "flex", alignItems: "center", gap: 1 }}
        >
          {loadingIncidents && <CircularProgress size={18} color="inherit" />}
          {loadingIncidents ? "Loading..." : "Get Incidents"}
        </MDButton>
      </MDBox>

      {showIncidents && (
        <MDBox pt={6} pb={3}>
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
                    Incidents
                  </MDTypography>
                </MDBox>
                <MDBox pt={3}>
                  <DataTable
                    table={{ columns: incidentColumns, rows: tableRows }}
                    isSorted={false}
                    entriesPerPage={false}
                    showTotalEntries={false}
                    noEndBorder
                  />
                </MDBox>
              </Card>
            </Grid>
          </Grid>
          <MDBox pt={3}>
            <MDButton
              color="info"
              variant="outlined"
              onClick={handleExportPowerPoint}
              disabled={loadingExport || selectedIncidents.length === 0}
              sx={{ display: "flex", alignItems: "center", gap: 1 }}
            >
              {loadingExport && (
                <CircularProgress size={18} color="inherit" thickness={5} />
              )}
              {loadingExport ? "Exporting..." : "Export to PowerPoint"}
            </MDButton>
          </MDBox>
        </MDBox>
      )}

      <Dialog
        open={openDialog}
        onClose={() => setOpenDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Incident Details</DialogTitle>
        <DialogContent dividers>
          {[
            "company",
            "executive_summary",
            "background",
            "malicious_activity",
            "outcomes_and_losses",
          ].map((field) => (
            <MDBox key={field} mb={2}>
              <MDTypography variant="subtitle2" color="text">
                {field
                  .replace(/_/g, " ")
                  .replace(/\b\w/g, (l) => l.toUpperCase())}
              </MDTypography>
              {isEditing ? (
                <MDInput
                  multiline
                  fullWidth
                  minRows={4}
                  value={selectedFunction[field]}
                  onChange={(e) =>
                    setSelectedFunction((prev) => ({
                      ...prev,
                      [field]: e.target.value,
                    }))
                  }
                  sx={{ mt: 0.5 }}
                />
              ) : (
                <MDTypography
                  variant="body2"
                  whiteSpace="pre-line"
                  sx={{ mt: 0.5 }}
                >
                  {selectedFunction[field] || "—"}
                </MDTypography>
              )}
            </MDBox>
          ))}

          {selectedFunction.source_url && (
            <MDBox mt={2}>
              <MDTypography variant="subtitle2" color="text">
                Source URL
              </MDTypography>
              <a
                href={selectedFunction.source_url}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "#1a73e8" }}
              >
                {selectedFunction.source_url}
              </a>
            </MDBox>
          )}
          {["hallucination_explanation", "summariser_explanation"].map(
            (field) => (
              <MDBox key={field} mb={2}>
                <MDTypography variant="subtitle2" color="text">
                  {field
                    .replace(/_/g, " ")
                    .replace(/\b\w/g, (l) => l.toUpperCase())}
                </MDTypography>
                <MDTypography
                  variant="body2"
                  whiteSpace="pre-line"
                  sx={{ mt: 0.5 }}
                >
                  {selectedFunction[field] || "—"}
                </MDTypography>
              </MDBox>
            )
          )}
        </DialogContent>

        <DialogActions>
          {isEditing ? (
            <MDButton
              color="success"
              variant="gradient"
              onClick={() => setIsEditing(false)}
            >
              Save
            </MDButton>
          ) : (
            <MDButton
              color="info"
              variant="outlined"
              onClick={() => setIsEditing(true)}
            >
              Edit
            </MDButton>
          )}
          <Button onClick={() => setOpenDialog(false)} color="primary">
            Close
          </Button>
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

export default Slides;
