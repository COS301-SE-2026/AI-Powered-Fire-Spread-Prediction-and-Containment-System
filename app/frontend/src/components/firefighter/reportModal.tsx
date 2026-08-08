import { Report } from "../../types/firefighter-dashboard"

interface fireReport{
    report: Report;
};

export function ReportModalTable({ report }: Readonly<fireReport>){
    return(
        <>
        {/* Open the modal using document.getElementById('ID').showModal() method */}
        <button type="button" className="btn btn-soft btn-neutral btn-outline rounded-full" onClick={()=>(document.getElementById('my_modal_2') as HTMLDialogElement | null)?.showModal()}>
            view
        </button>


        <dialog id="my_modal_2" className="modal">
            <div className="modal-box border border-carbon-stroke rounded-2xl">
                <div className="flex flex-col">
                    <h3 className="font-bold text-lg">Fire Reference Number:</h3>
                    <p className="py-4">{report.ref}</p>
                    <h3 className="font-bold text-lg">Fire Status:</h3>
                    <p className="py-4">{report.status}</p>
                    <div className="flex flex-row">
                        <h3 className="font-bold text-lg">Size:</h3>
                        <p className="py-4">{report.size} ha</p>
                        <h3 className="font-bold text-lg">Reporter:</h3>
                        <p className="py-4">{report.reporter}</p>
                    </div>
                </div>
            </div>
            <form method="dialog" className="modal-backdrop backdrop-blur-sm">
                <button type="submit">close</button>
            </form>
        </dialog>
        </>
    )
}