select patient_id, department, visit_type
from hospiotal_visits
Group by patient_id, department, visit_type
order by patient_id ASC;