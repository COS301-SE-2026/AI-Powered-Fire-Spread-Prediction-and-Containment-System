import { ComponentsGroup, Labled } from "./componentsGroup";

export function Toasts() {
  return <ComponentsGroup title="Toast Positioning">
            <div className="flex flex-wrap gap-6">
                <Labled caption="top-end">
                    <div
                        className="relative w-64 h-40 bg-carbon-side/40 rounded-xl border border-carbon-stroke overflow-hidden"
                        style={{ transform: 'translate(0)' }}
                    >
                        <div className="toast toast-top toast-end">
                            <div className="alert alert-success">
                                <span>Report submitted</span>
                            </div>
                        </div>
                    </div>
                </Labled>

                <Labled caption="bottom-end">
                    <div
                        className="relative w-64 h-40 bg-carbon-side/40 rounded-xl border border-carbon-stroke overflow-hidden"
                        style={{ transform: 'translate(0)' }}
                    >
                        <div className="toast toast-bottom toast-end">
                            <div className="alert alert-error">
                                <span>Submission failed</span>
                            </div>
                        </div>
                    </div>
                </Labled>
            </div>
        </ComponentsGroup>
}