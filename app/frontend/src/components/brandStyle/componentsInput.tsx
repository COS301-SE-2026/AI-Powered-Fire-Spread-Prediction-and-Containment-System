import { ComponentsGroup, Labled } from "./componentsGroup"

export function Input() {
    return (
        <>
            <ComponentsGroup title="Input States">
                <div className="flex flex-wrap justify-start items-start gap-4">
                    <Labled caption="default">
                        <input type="text" placeholder="example@something.co.za" className="input input-neutral w-96 text-text-primary focus:border-primary"/>
                    </Labled>
                    <Labled caption="focus (forced)">
                        <input type="text" placeholder="example@something.co.za" className="input input-neutral w-96 text-text-primary border-primary"/>
                    </Labled>
                    <Labled caption="error">
                        <div className="w-96">
                            <input type="text" placeholder="example@something.co.za" className="input input-error w-96"/>
                            <p className="text-error text-xs mt-1">Enter a valid address</p>
                        </div>
                    </Labled>
                    <Labled caption="disabled">
                        <input type="text" placeholder="example@something.co.za" disabled className="input input-bordered w-96"/>
                    </Labled>
                </div>
            </ComponentsGroup>
        </>
    );
}