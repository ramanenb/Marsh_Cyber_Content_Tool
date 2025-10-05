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
import Button from "@mui/material/Button";
import MenuItem from "@mui/material/MenuItem";
import IconButton from "@mui/material/IconButton";
import DeleteIcon from "@mui/icons-material/Delete";
import Checkbox from "@mui/material/Checkbox";
import CircularProgress from "@mui/material/CircularProgress";

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

function Slides() {
  const [loadingIncidents, setLoadingIncidents] = useState(false);
  const [loadingExport, setLoadingExport] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedFunction, setSelectedFunction] = useState("");
  const [incidentsData, setIncidentsData] = useState([]);
  const [incidentColumns] = useState([
    { Header: "", accessor: "select", width: "5%", align: "center" },
    { Header: "company", accessor: "company", width: "20%", align: "left" },
    {
      Header: "executive summary",
      accessor: "executive_summary",
      align: "left",
    },
    {
      Header: "hallucination likelihood",
      accessor: "hallucinationLikelihood",
      align: "center",
    },
    { Header: "action", accessor: "action", align: "center" },
  ]);
  const [showIncidents, setShowIncidents] = useState(false);

  // store indices of selected incidents
  const [selectedIncidents, setSelectedIncidents] = useState([]);

  const handleGetIncidents = async () => {
    setLoadingIncidents(true);
    try {
      const response = await fetch("/api/incidents.json");
      const data = await response.json();
      setIncidentsData(data);
      setShowIncidents(true);
      setSelectedIncidents([]);
    } catch (error) {
      console.error("Failed to fetch incidents:", error);
    } finally {
      setLoadingIncidents(false);
    }
  };

  const [isEditing, setIsEditing] = useState(false);

  const [industryOptions, setIndustryOptions] = useState([]);
  const [selectedIndustries, setSelectedIndustries] = useState([]);
  const [newIndustry, setNewIndustry] = useState("");
  useEffect(() => {
    const fetchIndustries = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/getIndustries");
        const data = await response.json();
        if (data.industries) setIndustryOptions(data.industries);
      } catch (error) {
        console.error("Failed to fetch industries:", error);
      }
    };
    fetchIndustries();
  }, []);

  const [newRegion, setNewRegion] = useState("");
  const [regionOptions] = useState([
    "Hong Kong SAR",
    "India",
    "Indonesia",
    "Japan",
    "Malaysia",
    "People's Republic of China",
    "Philippines",
    "Singapore",
    "South Korea",
    "Taiwan",
    "Thailand",
    "Vietnam",
  ]);
  const [clientContext, setClientContext] = useState("");

  const handleAddIndustry = () => {
    if (newIndustry && !selectedIndustries.includes(newIndustry)) {
      setSelectedIndustries([...selectedIndustries, newIndustry]);
      setNewIndustry("");
    }
  };

  const handleDeleteIndustry = (index) => {
    const updated = [...selectedIndustries];
    updated.splice(index, 1);
    setSelectedIndustries(updated);
  };

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
      company: item.affected_organization || "N/A",
      executive_summary: item.executive_summary || "—",
      hallucinationLikelihood: item.hallucinationLikelihood || "unknown",
      action: (
        <MDButton
          variant="outlined"
          color="info"
          size="small"
          onClick={() => {
            setSelectedFunction({
              executive_summary: item.executive_summary || "",
              background: item.background || "",
              malicious_activity: item.malicious_activity || "",
              outcomes_and_losses: item.outcomes_and_losses || "",
              source_url: item.source_url || "",
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

  const handleExportPowerPoint = async () => {
    setLoadingExport(true);
    try {
      // Simulate export logic
      await new Promise((resolve) => setTimeout(resolve, 1500));
      console.log("PowerPoint export triggered!");
    } catch (error) {
      console.error("Export failed:", error);
    } finally {
      setLoadingExport(false);
    }
  };
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
            label="Add Industry"
            value={newIndustry}
            onChange={(e) => setNewIndustry(e.target.value)}
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
          <MDButton color="info" variant="outlined" onClick={handleAddIndustry}>
            Add
          </MDButton>
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
              disabled={loadingExport}
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
    </DashboardLayout>
  );
}

export default Slides;
