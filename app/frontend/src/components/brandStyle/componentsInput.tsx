import { ComponentsGroup, Labled } from "./componentsGroup"

export function Input() {
  return <ComponentsGroup title="Input States">
            <div className="flex flex-wrap justify-start items-start gap-4">
                <Labled caption="default">
                    <div>
                        <label htmlFor="input-default" className="block text-sm text-text-muted mb-1">Email</label>
                        <input type="text" placeholder="example@something.co.za" className="input input-bordered w-96 item-center gap-2 border-carbon-stroke focus-within:outline-ignite focus-within:border-none h-11"/>
                    </div>
                </Labled>
                <Labled caption="focus (forced)">
                    <div>
                            <label htmlFor="input-focus" className="block text-sm text-text-muted mb-1">Email</label>
                        <input type="text" placeholder="example@something.co.za" className="input input-neutral w-96 text-text-primary border-primary"/>
                    </div>
                </Labled>
                <Labled caption="error">
                    <div className="w-96">
                        <label htmlFor="input-error" className="block text-sm text-text-muted mb-1">Email</label>
                        <input type="text" placeholder="example@something.co.za" className="input input-error w-96"/>
                        <p className="text-error text-xs mt-1">Enter a valid address</p>
                    </div>
                </Labled>
                <Labled caption="disabled">
                    <div>
                        <label htmlFor="input-disabled" className="block text-sm text-text-muted mb-1">Email</label>
                        <input type="text" placeholder="example@something.co.za" disabled className="input input-bordered w-96"/>
                    </div>
                </Labled>
            </div>
        </ComponentsGroup>
}