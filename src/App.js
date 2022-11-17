import { Helmet } from "react-helmet";

function App() {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        flexDirection: "column",
        background: "#131524",
        padding: 100,
      }}
    >
      <Helmet>
        <style>{"body { background-color: #131524; }"}</style>
      </Helmet>
      <h1 style={{ color: "#a1aad6" }}>Water Widget</h1>
      <div
        style={{
          background: "#292e47",
          borderRadius: 10,
          marginTop: 50,
          padding: 30,
          color: "white",
          textAlign: "center",
        }}
      >
        <h2 style={{ color: "#8890b8" }}>Moisture Level</h2>
        <div style={{ fontSize: 75, fontWeight: "bold", marginTop: -20 }}>50</div>
        <div style={{ fontSize: 20, fontWeight: "bold" }}>%</div>
      </div>
    </div>
  );
}

export default App;
