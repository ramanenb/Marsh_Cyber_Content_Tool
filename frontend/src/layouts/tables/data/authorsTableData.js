/* eslint-disable react/prop-types */
/* eslint-disable react/function-component-definition */
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

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDAvatar from "components/MDAvatar";
import MDBadge from "components/MDBadge";

// Images
import team2 from "assets/images/team-2.jpg";
import team3 from "assets/images/team-3.jpg";
import MDButton from "components/MDButton";

export default function data() {
  const Author = ({ image, name, email }) => (
    <MDBox display="flex" alignItems="left" lineHeight={1}>
      {/* <MDAvatar src={image} name={name} size="sm" /> */}
      <MDBox ml={0} lineHeight={1}>
        <MDTypography display="block" variant="button" fontWeight="medium">
          {name}
        </MDTypography>
        <MDTypography variant="caption">{email}</MDTypography>
      </MDBox>
    </MDBox>
  );

  const Job = ({ title, description }) => (
    <MDBox lineHeight={1} textAlign="left">
      <MDTypography display="block" variant="caption" color="text" fontWeight="medium">
        {title}
      </MDTypography>
      <MDTypography variant="caption">{description}</MDTypography>
    </MDBox>
  );

  return {
    columns: [
      { Header: "Victim", accessor: "Victim", width: "45%", align: "left"},
      { Header: "Industry", accessor: "Industry", align: "left" },
      { Header: "Event date", accessor: "Event_date", align: "center" },
      { Header: "Event type", accessor: "Event_type", align: "center" },
      { Header: "Attacker", accessor: "Attacker", align: "center" },
      { Header: "Attacker Origin", accessor: "Attacker_Origin", align: "center" },
      { Header: "Victim Origin", accessor: "Victim_Origin", align: "center" },
      { Header: "Motive", accessor: "Motive", align: "center" },  
      { Header: "Description", accessor: "Description", align: "center" },
      { Header: "Source", accessor: "Source_Link", align: "center" },                   
    ],

    rows: [
      {
        Victim: <Author name="Bell Group"/>,
        Industry: <Job title="Real Estate" description="Real Estate and Rental and Leasing" />,
        Event_date: (
          <MDTypography variant="h6" color="text" fontWeight="medium">
            28-12-2023
          </MDTypography>
        ),
        Event_type: (
          <MDBox ml={-1}>
            <MDBadge badgeContent="Exploitation of Application Server" color="warning" variant="gradient" size="lg" />
          </MDBox>
        ),
        Attacker: <Author name="Cactus" email="Criminal"/>,
        Attacker_Origin: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            Undetermined
          </MDTypography>
        ),
        Victim_Origin: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            United Kingdom of Great Britain and Northern Ireland
          </MDTypography>
        ),
        Motive: (
          <MDTypography variant="h6" color="text" fontWeight="medium">
            Financial
          </MDTypography>
        ),
        Description: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            The Cactus ransomware gang claims responsibility for a ransomware attack to Bell Group.
          </MDTypography>
        ),
        Source_Link: (
          <MDTypography component="a" href="https://twitter.com/FalconFeedsio/status/1740719323117686820" variant="button" color="text" fontWeight="medium">
            Link
          </MDTypography>
        ),
      },
      {
        Victim: <Author name="SnappFood"/>,
        Industry: <Job title="Food" description="Accommodation and Food Services" />,
        Event_date: (
          <MDTypography variant="h6" color="text" fontWeight="medium">
            30-12-2023
          </MDTypography>
        ),
        Event_type: (
          <MDBox ml={-1}>
            <MDBadge badgeContent="Exploitation of Application Server" color="warning" variant="gradient" size="lg" />
          </MDBox>
        ),
        Attacker: <Author name="Irleaks" email="Criminal"/>,
        Attacker_Origin: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            Undetermined
          </MDTypography>
        ),
        Victim_Origin: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            Iran (Islamic Republic of)
          </MDTypography>
        ),
        Motive: (
          <MDTypography variant="h6" color="text" fontWeight="medium">
            Financial
          </MDTypography>
        ),
        Description: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            Irleaks claims to have broken into the systems of SnappFood, Iran's le…
          </MDTypography>
        ),
        Source_Link: (
          <MDTypography component="a" href="https://www.darkreading.com/cyberattacks-data-breaches/pilfered-data-from-iranian-insurance-and-food-delivery-firms-leaked" variant="button" color="text" fontWeight="medium">
            Link
          </MDTypography>
        ),
      },
      ,
      {
        Victim: <Author name="Reinsel Kuntz Lesher"/>,
        Industry: <Job title="Services" description="Professional, Scientific, and Technical Services" />,
        Event_date: (
          <MDTypography variant="h6" color="text" fontWeight="medium">
            28-12-2023
          </MDTypography>
        ),
        Event_type: (
          <MDBox ml={-1}>
            <MDBadge badgeContent="Exploitation of Application Server" color="warning" variant="gradient" size="lg" />
          </MDBox>
        ),
        Attacker: <Author name="Irleaks" email="Criminal"/>,
        Attacker_Origin: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            Undetermined
          </MDTypography>
        ),
        Victim_Origin: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            United States of America
          </MDTypography>
        ),
        Motive: (
          <MDTypography variant="h6" color="text" fontWeight="medium">
            Financial
          </MDTypography>
        ),
        Description: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            Reinsel Kuntz Lesher (RKL) files a notice of data breach after discovering that an unauthorized party was able to access confidential information
          </MDTypography>
        ),Source_Link: (
          <MDTypography component="a" href="https://www.jdsupra.com/legalnews/reinsel-kuntz-lesher-llp-files-official-5712335/" variant="button" color="text" fontWeight="medium">
            Link
          </MDTypography>
        ),
      }
    ],
  };
}
