/**
=========================================================
* Material Dashboard 2 React - v2.2.0
=========================================================

* Product Page: https://www.creative-tim.com/product/material-dashboard-react
* Copyright 2023 Creative Tim (https://www.creative-tim.com)

Coded by www.creative-tim.com

 =========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/

// @mui material components
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MenuItem from "@mui/material/MenuItem";
import IconButton from "@mui/material/IconButton";
import DeleteIcon from "@mui/icons-material/Delete";
import MDButton from "components/MDButton";

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import DataTable from "examples/Tables/DataTable";

// state
import { useState, useEffect } from "react";

function Slides() {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedFunction, setSelectedFunction] = useState("");
  const [incidentRows, setIncidentRows] = useState([]);
  const [incidentColumns] = useState([
    { Header: "company", accessor: "company", width: "25%", align: "left" },
    { Header: "details", accessor: "details", align: "left" },
    {
      Header: "hallucination likelihood",
      accessor: "hallucinationLikelihood",
      align: "left",
    },
    { Header: "action", accessor: "action", align: "center" },
  ]);
  const [showIncidents, setShowIncidents] = useState(false);

  const handleGetIncidents = async () => {
    try {
      const response = await fetch("/api/incidents.json");
      const data = await response.json();

      const newRows = data.map((item) => {
        // take first 5 words for the snippet
        const snippet = item.details.split(" ").slice(0, 5).join(" ") + "...";

        return {
          company: item.company,
          hallucinationLikelihood: item.hallucinationLikelihood,
          details: snippet, // snippet column
          action: (
            <MDButton
              variant="outlined"
              color="info"
              size="small"
              onClick={() => {
                setSelectedFunction(item.details); // full text
                setOpenDialog(true);
              }}
            >
              View
            </MDButton>
          ),
        };
      });

      setIncidentRows(newRows);
      setShowIncidents(true);
    } catch (error) {
      console.error("Failed to fetch incidents:", error);
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
        if (data.industries) {
          setIndustryOptions(data.industries);
        }
      } catch (error) {
        console.error("Failed to fetch industries:", error);
      }
    };

    fetchIndustries();
  }, []);

  const [newRegion, setNewRegion] = useState("");
  const [regionOptions, setRegionOptions] = useState([
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
                setUploadedFiles((prev) => [...prev, ...uploaded]); // append files
              }}
            />
          </MDButton>

          {/* Show Uploaded Files */}
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
                      onClick={() => {
                        setUploadedFiles((prev) =>
                          prev.filter((_, i) => i !== idx)
                        );
                      }}
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

        {/* Selected industries */}
        <MDBox display="flex">
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

        {/* Add new industry */}
        <MDBox display="flex">
          <MDBox display="flex" gap={1} flexWrap="wrap" mt={1}>
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
            <MDButton
              color="info"
              variant="outlined"
              onClick={handleAddIndustry}
            >
              Add
            </MDButton>
          </MDBox>
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
      <MDBox px={3} pt={2}>
        <MDButton color="info" variant="outlined" onClick={handleGetIncidents}>
          Get Incidents
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
                    table={{ columns: incidentColumns, rows: incidentRows }}
                    isSorted={false}
                    entriesPerPage={false}
                    showTotalEntries={false}
                    noEndBorder
                  />
                </MDBox>
              </Card>
            </Grid>
          </Grid>
          <MDBox px={3} pt={2}>
            <MDButton color="info" variant="outlined">
              Export to Powerpoint
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
          {isEditing ? (
            <MDInput
              multiline
              fullWidth
              minRows={8}
              value={selectedFunction}
              onChange={(e) => setSelectedFunction(e.target.value)}
            />
          ) : (
            <MDTypography variant="body2" whiteSpace="pre-line">
              {selectedFunction}
            </MDTypography>
          )}
        </DialogContent>
        <DialogActions>
          {isEditing ? (
            <MDButton
              color="success"
              variant="gradient"
              onClick={() => setIsEditing(false)} // save changes
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
