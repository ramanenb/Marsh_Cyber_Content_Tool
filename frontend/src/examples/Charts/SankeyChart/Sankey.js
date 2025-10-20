import React, { useMemo } from "react";
import { Chart } from "react-google-charts";

import Card from "@mui/material/Card";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

// configs
import configs from "./Config/SankeyConfig";

export default function SankeyChart({ color, chart, title, description }) {
  const { options } = configs();

  const chartMemo = useMemo(
    () => (
      <MDBox
        variant="gradient"
        bgColor={color}
        borderRadius="lg"
        coloredShadow={color}
        py={2}
        pr={0.5}
        mt={-5}
        px={3}
        height="16.5rem"
      >
        <Chart
          chartType="Sankey"
          width="100%"
          height="100%"
          data={chart.data}
          options={options}
        />
      </MDBox>
    ),
    [chart, color, options]
  );

  return (
    <Card sx={{ height: "100%", width: "100%", padding: "1rem" }}>
      <MDBox padding="1rem">
        {chartMemo}
        <MDBox pt={3} textAlign="center">
          <MDTypography variant="h6" textTransform="capitalize">
            {title}
          </MDTypography>
          <MDTypography
            component="div"
            variant="button"
            color="text"
            fontWeight="light"
          >
            {description}
          </MDTypography>
        </MDBox>
      </MDBox>
    </Card>
  );
}
