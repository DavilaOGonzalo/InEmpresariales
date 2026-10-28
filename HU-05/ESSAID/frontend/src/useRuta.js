import { useCallback, useEffect, useState } from 'react';

export function useRuta() {
  const [ruta, setRuta] = useState(() => window.location.pathname);

  useEffect(() => {
    const actualizar = () => setRuta(window.location.pathname);
    window.addEventListener('popstate', actualizar);
    return () => window.removeEventListener('popstate', actualizar);
  }, []);

  const navegar = useCallback((destino, reemplazar = false) => {
    if (reemplazar) window.history.replaceState({}, '', destino);
    else window.history.pushState({}, '', destino);
    setRuta(destino);
  }, []);

  return [ruta, navegar];
}
