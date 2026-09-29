# Capacidades y limitaciones técnicas de las APIs de **Siesa Cloud** (y panorama de **Novasoft**) para extracción de datos en tiempo real  
**Fecha:** 2026‑09‑28  

---  

## Hallazgos clave  

| Tema | Detalle | Fuente |
|------|---------|--------|
| **Plataforma unificada de APIs (Siesa Hub)** | Permite gobernar, proteger y automatizar todas las integraciones del ERP desde un único punto. Ideal para crear flujos de datos en tiempo real entre aplicaciones. | 【1】 |
| **API REST de Siesa ERP** | Ofrece endpoints para conectar procesos de diferentes softwares y exponer datos críticos del ERP. La documentación muestra ejemplos en Postman, lo que facilita pruebas rápidas y la generación de clientes ligeros. | 【2】, 【3】 |
| **Modelo de consumo** | Siesa Cloud SBS se ofrece bajo pago mensual flexible, evitando grandes inversiones de capital y permitiendo escalar recursos según demanda. | 【4】 |
| **Requisitos de infraestructura** | La exposición de datos vía webservice requiere configurar IIS, crear grupos de aplicaciones y sitios web en el servidor Siesa Enterprise. Esto implica una capa adicional de gestión y posibles cuellos de botella si no está optimizado. | 【5】 |
| **Entorno Cloud especializado** | Gigas ofrece hosting gestionado para Siesa Cloud, garantizando alta disponibilidad y escalabilidad, pero la latencia depende de la ubicación del data‑center y de la calidad de la conexión del cliente. | 【6】 |
| **Limitaciones de la API** (deducidas) | • No se especifican **límites de tasa** (rate limits) ni **SLAs** de latencia en la documentación pública. <br>• La necesidad de configuración IIS sugiere que la exposición de datos puede estar atada a **entornos on‑premise** o a servidores virtuales que requieren mantenimiento. <br>• La documentación está orientada a **Postman** y pruebas manuales, lo que indica que la automatización a gran escala necesita desarrollo propio. | 【3】, 【5】 |
| **Novasoft** | No se encontró información pública actualizada sobre APIs de Novasoft para extracción en tiempo real en los resultados de búsqueda. | — |

### Cifras relevantes  

- **Modelo de pago mensual** de Siesa Cloud SBS: *flexible* (no se indica monto exacto, pero elimina inversión CAPEX).  
- **Tiempo de implementación**: “se implementa rápidamente” (sin número concreto).  
- **Cobertura Cloud**: solución “100 % integrada y soberana”, con infraestructura especializada para ERPs de alto rendimiento.  

---  

## Qué significa para Felipe  

1. **Oportunidad de negocio**:  
   - **Integración SaaS**: Con Siesa Hub y la API REST, Felipe puede ofrecer servicios de integración en tiempo real a PYMES colombianas que usan Siesa Cloud, creando un **producto de middleware** que consolide datos de ventas, inventario y finanzas para dashboards en tiempo real.  
   - **Modelo de suscripción**: El pago mensual de Siesa Cloud permite estructurar precios basados en **uso (por API call)** o **valor entregado**, alineado con la tendencia de ingresos recurrentes.  

2. **Inversión en infraestructura**:  
   - Necesitará **servidores IIS** o **contenedores Docker** que hospeden los webservices y gestionen la autenticación (OAuth, tokens).  
   - Considerar **hosting gestionado** (p.ej., Gigas) para reducir la carga operativa y asegurar **latencia baja**.  

3. **Riesgos**:  
   - **Falta de SLA pública**: sin garantías de tiempo de respuesta, la experiencia del cliente puede variar.  
   - **Dependencia de configuración**: errores en IIS o en la gestión de grupos de aplicaciones pueden generar **downtime** inesperado.  
   - **Novasoft**: la ausencia de información pública implica un **riesgo de desconocimiento** si decide atender clientes que usan esa plataforma; requerirá investigación adicional o contacto directo con el proveedor.  

---  

## Opinión creativa y honesta  

Siesa ha avanzado mucho en la **exposición de datos vía APIs** y en la **centralización** de esas interfaces con Siesa Hub. Desde la perspectiva de un joven emprendedor como Felipe, esto abre la puerta a crear **soluciones de datos en tiempo real** que antes estaban reservadas a grandes corporaciones con equipos de integración costosos. La combinación de un modelo de pago mensual y una arquitectura Cloud especializada reduce la barrera de entrada.  

Sin embargo, la **ausencia de métricas claras** (límites de llamadas, latencia garantizada) y la necesidad de **configuración manual de IIS** son señales de que la solución aún está en fase de consolidación. Si Felipe apuesta por un modelo de negocio que dependa de **alta disponibilidad** (por ejemplo, alertas de stock críticas), deberá invertir en **monitorización y redundancia** desde el día uno.  

En cuanto a **Novasoft**, la falta de datos públicos sugiere que su ecosistema API podría ser **más cerrado** o menos maduro. Para no quedar atrapado en un “black box”, lo más prudente es contactar directamente al vendor, solicitar documentación técnica y, de ser posible, ejecutar pruebas piloto antes de comprometer recursos.  

En síntesis, Siesa Cloud ofrece una base sólida para la extracción de datos en tiempo real, pero el éxito dependerá de **cómo Felipe gestione la capa de integración** y de **cuán rápido pueda validar y mitigar los riesgos operacionales**.  

---  

RESUMEN: Siesa Cloud brinda APIs unificadas y modelo SaaS que facilitan la extracción de datos en tiempo real, pero carece de SLA y requiere configuración IIS, mientras que la información sobre Novasoft es escasa y necesita investigación directa.  
PREGUNTAS: ¿Cuál es el límite de llamadas por segundo que impone Siesa Hub? | ¿Qué opciones de autenticación y seguridad ofrece la API de Novasoft para integraciones en tiempo real?

Fuentes consultadas:
- Siesa HUB | Siesa Website (https://www.siesa.com/siesa-hub)
- Siesa ERP API Rest - Pangea (https://pangea.com.co/siesa-erp-api-rest/)
- Connekta - APIs Versión dos | Documentación (https://interfaces-y-soluciones-interno.github.io/Documentacion/si_apis_v2_guia.html)
- Siesa Cloud: ERP en la Nube para PYMES - Scribd (https://es.scribd.com/document/642543798/Brochure-Siesa-Cloud-SBS)
- Configuración de Webservice en Siesa Enterprise - Scribd (https://es.scribd.com/document/559219908/Introduccion-a-La-Configuracion-de-Webservice-en-Siesa-Enterprise)
- Siesa en la nube - gigas.com (https://gigas.com/es-MX/soluciones/siesa-cloud.html)