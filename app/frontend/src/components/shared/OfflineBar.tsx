import React, { useEffect, useState } from 'react';
import { probeHealth } from '../../lib/offline/shared';
import { offlineStore } from '../../lib/offlineStore';

export const OfflineBar: React.FC = () => {
    const[isOffline, setIsOffline] = useState(false);
    const [queueCount, setQueueCount] = useState(0);
}