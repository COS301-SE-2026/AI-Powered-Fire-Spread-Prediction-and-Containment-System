import { useUserInfo } from '../../hooks/useUserInfo';

export default function ProfilePage(){
    const { user, isLoading} = useUserInfo();

    let name = "";
    let initial = "";
    if (user) {
        name = `${user.name} ${user.surname}`;
        initial = user.name.charAt(0);
    } else if (isLoading) {
        name = "Loading...";
        initial = "?";
    } else {
        name = "Not signed in";
        initial = "?";
    }
    return (
        <div className='p-6'>
            <div className='flex items-center gap-8 mt-6 mb-8 pb-8 bg-card'>
                <div className='w-20 h-20 rounded-full bg-ignite flex items-center justify-center text-2xl font-display font-bold text-char shrink-0'>{initial}</div>
                <div className="min-w-0">
                    <h1 className="text-text-primary uppercase">{name}</h1>
                    {user ? (
                        <h4 className="text-text-muted mt-0.5 uppercase">{user.role}</h4>
                    ) : null}
                </div>
            </div>
        </div>
    );
}