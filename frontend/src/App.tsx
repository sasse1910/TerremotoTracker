/**
 * Componente raiz da aplicação.
 * FASE 1: Placeholder simples para validar que o frontend sobe.
 * FASE 3: Será substituído pelo layout completo com mapa + painel.
 */

function App() {
  return (
    <div className="flex h-full items-center justify-center bg-gray-900">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white mb-4">
          🌋 TerremotoTracker
        </h1>
        <p className="text-gray-400 text-lg">
          Monitor Sísmico Global — FASE 1 operacional
        </p>
        <div className="mt-6 flex gap-4 justify-center">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            API Docs
          </a>
          <a
            href="http://localhost:8000/health"
            target="_blank"
            rel="noreferrer"
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition"
          >
            Health Check
          </a>
        </div>
      </div>
    </div>
  );
}

export default App;
