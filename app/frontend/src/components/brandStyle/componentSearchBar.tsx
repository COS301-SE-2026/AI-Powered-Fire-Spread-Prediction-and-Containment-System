"use client";

import { useState } from "react";
import { ComponentsGroup, Labled } from "./componentsGroup";
import { SearchBar } from "../admin/searchBar";

export function SearchBarComponents() {
    const [value, setValue] = useState("");

    return (
        <ComponentsGroup title="Search Bar">
            <div className="flex flex-wrap justify-center">
                <Labled caption="default">
                    <SearchBar value={value} onChange={setValue} />
                </Labled>
            </div>
        </ComponentsGroup>
    );
}