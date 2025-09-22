interface MeasurementGridProps {
  measurements: any[];
}

const MeasurementGrid: React.FC<MeasurementGridProps> = ({ measurements }) => {
  console.log(measurements)
  return (
    <div className="measurement-grid">
      {measurements.map((m, i) => (
        <div key={i} className="measurement-card">
          <div className="measurement-label">{m.organo}</div>
          <div className="measurement-label">{m.tipo_medicion}</div>
          
          <div className="measurement-value">
            {m.valor} {m.unidad ?? ""}
          </div>
        </div>
      ))}
    </div>
  );
};

export default MeasurementGrid