import { PageHeader } from "../layout/pageHeader";

export default function ProfilePage({ showHeaderIcons = true }){
    return (
        <div>
            <PageHeader title="Register a Resource" subtitle="Add your water trailer, tank, dam, hydrant, crew or equipment to be used in a fire." showIcons={showHeaderIcons} />
        </div>
    );
}