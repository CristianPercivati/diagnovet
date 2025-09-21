from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time

# Métrica 1: Contador de operaciones de diagnóstico
diagnosis_counter = Counter(
    'diagnovet_diagnosis_operations_total',
    'Total number of diagnosis operations',
    ['operation', 'status']
)

# Métrica 2: Tiempo de respuesta de operaciones
diagnosis_duration = Histogram(
    'diagnovet_diagnosis_duration_seconds',
    'Duration of diagnosis operations in seconds',
    ['operation'],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Métrica 3: Estado de la base de datos
database_status = Gauge(
    'diagnovet_database_status',
    'Database connection status (1=up, 0=down)',
    ['database_type']
)

class MetricsCollector:
    def __init__(self):
        self.start_time = time.time()
    
    def record_diagnosis_operation(self, operation: str, status: str, duration: float = None):
        """Registrar operación de diagnóstico"""
        diagnosis_counter.labels(operation=operation, status=status).inc()
        
        if duration is not None:
            diagnosis_duration.labels(operation=operation).observe(duration)
    
    def update_database_status(self, database_type: str, is_up: bool):
        """Actualizar estado de la base de datos"""
        database_status.labels(database_type=database_type).set(1 if is_up else 0)
    
    def get_metrics(self) -> str:
        """Obtener métricas en formato Prometheus"""
        return generate_latest()

# Instancia global del collector
metrics_collector = MetricsCollector()