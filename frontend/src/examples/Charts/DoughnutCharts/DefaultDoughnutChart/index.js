/**
=========================================================
* Dashboard - Donut Chart Component 
=========================================================
*/

import { useMemo } from "react";

// porp-types is a library for typechecking of props
import PropTypes from "prop-types";

// react-chartjs-2 components
import { Doughnut } from "react-chartjs-2";
import { Chart as ChartJS, 
  ArcElement, 
  Tooltip, 
  Legend 
} from "chart.js";

// @mui material components
import Card from "@mui/material/Card";
import Icon from "@mui/material/Icon";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

// DefaultDoughnutChart configurations
import configs from "examples/Charts/DoughnutCharts/DefaultDoughnutChart/configs";

ChartJS.register(ArcElement, Tooltip, Legend);

function DefaultDoughnutChart({ color, icon, title, description, chart }) {
  const { data, options } = configs(chart.labels || [], chart.datasets || {}, chart.cutout, title);

  return (
    <Card sx={{ height: "100%"}}>
      <MDBox padding = "1rem">
        {useMemo(
          () => (
            <MDBox
              variant="gradient"
              bgColor={color}
              borderRadius="lg"
              coloredShadow={color}
              py={2}
              pr={0.5}
              mt={-5}
              height="16.5rem"
            >
              <Doughnut data={data} options={options} redraw />
            </MDBox>
          ),
          [chart, color]
        )}
        
        <MDBox pt={3} pb={1} px={1}>
          <MDTypography variant="h6" textTransform="capitalize">
            {title}
          </MDTypography>
          <MDTypography component="div" variant="button" color="text" fontWeight="light">
            {description}
          </MDTypography>
        </MDBox>
      </MDBox>
    </Card>
  );
}

// function DefaultDoughnutChart({ icon, title, description, height, chart }) {
//   const { data, options } = configs(chart.labels || [], chart.datasets || {}, chart.cutout);

//   const renderChart = (
//     <Card sx={{ height: "100%" , width: "100%"}}>
//       <MDBox py={2} pr={2} pl={icon.component ? 1 : 2}>
//         {title || description ? (
//           <MDBox display="flex" px={description ? 1 : 0} pt={description ? 1 : 0}>
//             {icon.component && (
//               <MDBox
//                 width="4rem"
//                 height="4rem"
//                 bgColor={icon.color || "dark"}
//                 variant="gradient"
//                 coloredShadow={icon.color || "dark"}
//                 borderRadius="xl"
//                 display="flex"
//                 justifyContent="center"
//                 alignItems="center"
//                 color="white"
//                 mt={-5}
//                 mr={2}
//               >
//               </MDBox>
//             )}
//             <MDBox mt={icon.component ? -2 : 0}>
//               {title && <MDTypography variant="h6">{title}</MDTypography>}
//               <MDBox mb={2}>
//                 <MDTypography component="div" variant="button" color="text">
//                   {description}
//                 </MDTypography>
//               </MDBox>
//             </MDBox>
//           </MDBox>
//         ) : null}
//         {useMemo(
//           () => (
//             <MDBox height="16.5rem">
//               <Doughnut data={data} options={options} redraw />
//             </MDBox>
//           ),
//           [chart, height]
//         )}
//       </MDBox>
//     </Card>
//   );

//   return title || description ? <Card>{renderChart}</Card> : renderChart;
// }

// Setting default values for the props of DefaultDoughnutChart
DefaultDoughnutChart.defaultProps = {
  icon: { color: "info", component: "" },
  title: "",
  description: "",
};

// Typechecking props for the DefaultDoughnutChart
DefaultDoughnutChart.propTypes = {
  icon: PropTypes.shape({
    color: PropTypes.oneOf([
      "primary",
      "secondary",
      "info",
      "success",
      "warning",
      "error",
      "light",
      "dark",
    ]),
    component: PropTypes.node,
  }),
  title: PropTypes.string,
  description: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  height: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  chart: PropTypes.objectOf(PropTypes.oneOfType([PropTypes.array, PropTypes.object])).isRequired,
};

export default DefaultDoughnutChart;
