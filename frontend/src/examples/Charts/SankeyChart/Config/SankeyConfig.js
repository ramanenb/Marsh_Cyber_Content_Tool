function configs() {
    return {
        sankey: {
            node: {
            // Hide text labels
            label: { color: "transparent" },
            // Optional: give nodes a clean style
            nodePadding: 30,
            interactivity: true,
            },
            link: {
            colorMode: "gradient",
            },
        },
        tooltip: {
            isHtml: true, // Tooltips still appear
        },
    }
}

export default configs;