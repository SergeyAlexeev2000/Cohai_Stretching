import React, { useEffect, useMemo, useState } from 'react';
import {
  fetchLocations,
  fetchProgramTypes,
  fetchSchedule,
  fetchMemberships,
  createGuestVisit,
} from './api';
import { LocationSelect } from './components/LocationSelect';
import { ScheduleList } from './components/ScheduleList';
import { MembershipList } from './components/MembershipList';
import { LeadForm } from './components/LeadForm';

function App() {
  const [locations, setLocations] = useState([]);
  const [programTypes, setProgramTypes] = useState([]);
  const [selectedLocationId, setSelectedLocationId] = useState(null);

  const [schedule, setSchedule] = useState([]);
  const [memberships, setMemberships] = useState([]);

  const [loading, setLoading] = useState(true);
  const [leadStatus, setLeadStatus] = useState('');

  const programTypesById = useMemo(() => {
    const map = {};
    for (const pt of programTypes) {
      map[pt.id] = pt.name;
    }
    return map;
  }, [programTypes]);

  // Загружаем локации и типы программ при старте
  useEffect(() => {
    async function init() {
      try {
        setLoading(true);
        const [locs, pts] = await Promise.all([
          fetchLocations(),
          fetchProgramTypes(),
        ]);
        setLocations(locs);
        setProgramTypes(pts);
        if (locs.length > 0) {
          setSelectedLocationId(locs[0].id);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  // При смене локации подгружаем расписание и абонементы
  useEffect(() => {
    if (!selectedLocationId) return;

    async function loadData() {
      try {
        const [sch, mem] = await Promise.all([
          fetchSchedule(selectedLocationId),
          fetchMemberships(selectedLocationId),
        ]);
        setSchedule(sch);
        setMemberships(mem);
      } catch (e) {
        console.error(e);
      }
    }

    loadData();
  }, [selectedLocationId]);

  async function handleCreateLead(payload) {
    try {
      setLeadStatus('Отправляем заявку...');
      const result = await createGuestVisit(payload);
      setLeadStatus(`Заявка отправлена! ID лида: ${result.id}`);
    } catch (e) {
      console.error(e);
      setLeadStatus('Ошибка при отправке заявки');
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-xl text-white">
        Загрузка...
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 text-white">
      <h1 className="text-4xl font-bold mb-8">Cohai Stretching — Frontend</h1>

      {locations.length > 0 && (
        <>
          <h2 className="text-2xl font-semibold mb-4">1. Выберите локацию</h2>
          <LocationSelect
            locations={locations}
            value={selectedLocationId}
            onChange={setSelectedLocationId}
          />
        </>
      )}

      <h2 className="text-2xl font-semibold mt-10 mb-4">2. Расписание</h2>
      <ScheduleList
        schedule={schedule}
        programTypesById={programTypesById}
      />

      <h2 className="text-2xl font-semibold mt-10 mb-4">3. Абонементы</h2>
      <MembershipList memberships={memberships} />

      <h2 className="text-2xl font-semibold mt-10 mb-4">
        4. Записаться на гостевой визит
      </h2>
      <LeadForm
        locationId={selectedLocationId}
        programTypes={programTypes}
        onSubmit={handleCreateLead}
      />

      {leadStatus && (
        <p className="mt-4 text-blue-400 text-lg">{leadStatus}</p>
      )}
    </div>
  );
}

export default App;
