import React, { useState } from 'react';
import Card from '../Card';
import Button from '../Button';

interface RoleRequest {
  id: string;
  email: string;
  currentRole: string;
  requestedRole: 'Firefighter' | 'Admin';
  timestamp: string;
}