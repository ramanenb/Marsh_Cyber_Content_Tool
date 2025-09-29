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

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import IconButton from "@mui/material/IconButton";
import DeleteIcon from "@mui/icons-material/Delete";
import MDButton from "components/MDButton";

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";

// state
import { useState, useCallback } from "react";
function Repo() {
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [dragActive, setDragActive] = useState(false);
  
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
  
    return (
      <DashboardLayout>
        <DashboardNavbar />
        <MDBox px={3} pt={3}>
          <MDTypography variant="h6">Upload Proprietary Data (Optional)</MDTypography>
  
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
                          setUploadedFiles((prev) => prev.filter((_, i) => i !== idx))
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
      </DashboardLayout>
    );
  }
  
  export default Repo;