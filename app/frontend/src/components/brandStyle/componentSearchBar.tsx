'use client';

import { useState } from 'react';
import { ComponentsGroup, Labled } from './componentsGroup';
import { SearchBar } from '../shared/Searchbar';

export function SearchBarComponents() {
  const [value, setValue] = useState('');

  return (
    <ComponentsGroup title="Search Bar">
      <div className="flex flex-wrap justify-center">
        <Labled caption="default">
          <SearchBar value={value} placeholder="Search..." onChange={setValue} />
        </Labled>
      </div>
    </ComponentsGroup>
  );
}
