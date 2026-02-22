import { useState, useEffect } from 'react';
import { fetchCarriers, fetchCarrierDetail } from '../api/client';
import CarrierList from '../components/carriers/CarrierList';
import CarrierDetail from '../components/carriers/CarrierDetail';

export default function CarrierCRM() {
  const [carriers, setCarriers] = useState([]);
  const [selected, setSelected] = useState(null);
  const [detail, setDetail] = useState(null);
  const selectedCarrier = carriers.find((c) => c.mc_number === selected);

  useEffect(() => {
    fetchCarriers().then(setCarriers);
  }, []);

  useEffect(() => {
    if (selected) {
      fetchCarrierDetail(selected).then(setDetail);
    } else {
      setDetail(null);
    }
  }, [selected]);

  return (
    <div className="flex bg-surface border border-border" style={{ height: 'calc((100vh - 128px) / 0.75)' }}>
      <CarrierList carriers={carriers} selected={selected} onSelect={setSelected} />
      <CarrierDetail detail={detail} fallbackFriction={selectedCarrier?.friction} />
    </div>
  );
}
