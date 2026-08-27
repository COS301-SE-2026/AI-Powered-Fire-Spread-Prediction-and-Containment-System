
interface TeamMember {
    name: string;
    role: string;
    bio: string;
    image: string;
}

const teamMembers: TeamMember[] = [
    {
        name: 'Megan Lai',
        role: 'Team Lead, Integration Engineer, Testing Engineer',
        bio: 'As a final-year Computer Science and Data Science student, I am a driven problem-solver who thrives on tackling complex technical challenges. While I possess a solid foundation in frontend technologies, my primary expertise and professional passion lie in backend development. I am always looking for ways to expand my knowledge and learn new skills in order to build innovative and impactful solutions.',
        image: '/images/team/Megan.jpeg',
    },
    {
        name: 'Ryan Lynn',
        role: 'Ui Engineer, Backend Engineer, Data Engineer',
        bio: 'I am a final-year Computer Science student with a strong focus on backend development and system design. I take a structured and analytical approach to solving complex technical problems, with a particular interest in building efficient, scalable, and well-architected systems. ',
        image: '/images/team/Ryan.jpg',
    },
    {
        name: 'Inge Keyser',
        role: 'Testing Engineer',
        bio: 'I am a results-oriented BSc Computer Science student at the University of Pretoria with a strong foundation in data analysis, programming, and mathematics. I am passionate about leveraging data-driven insights to solve complex problems and am always looking to apply and expand my skills in Data Science. I am quick to adapt and master new technologies, I apply creative problemsolving skills and demonstrate high enthusiasm when tackling new projects. ',
        image: '/images/team/Inge.jpg',
    },
    {
        name: 'Janri du Toit',
        role: 'UI Engineer',
        bio: 'I am a final-year student with a growing interest and curiosity in all the facets of Computers Science. I gravitate more towards AI and data science where algorithms don\'t just solve problems, they uncover them. To me, the ability of a well-trained model to reveal invisible patterns, optimizing system performance and offering solutions to real-world challenges, is where logic meets true impact. ',
        image: '/images/team/Janri.jpg',
    },
    {
        name: 'Marco de Wit',
        role: 'UI Engineer, Integration Engineer',
        bio: 'I am a final-year Mathematics student with a strong foundation in software development, specialising in C++, TypeScript, and Python. I bring a combination of analytical thinking and practical problem-solving, allowing me to design efficient and optimised solutions grounded in mathematical principles',
        image: '/images/team/Marco.jpg',
    }
]

export function Team() {
    
    return (
        <div className='flex flex-wrap justify-center content-center gap-8'>
            {teamMembers.map((member, idx) => (
                <div key={idx} className="hover-3d cursor-pointer group">
                    {/* content */}
                    <figure className="w-80 rounded-2xl overflow-hidden bg-carbon-card border border-carbon-stroke group-hover:border-primary/50 shadow-2xl relative">
                        <img 
                            src={member.image}
                            alt={member.name}
                            className='object-cover transition-transform duration-500 group-hover:scale-105'
                            sizes='(max-width: 768px) 100vw, 320px'
                        />

                        <div className='p-5 text-left bg-carbon-card'>
                            <h3 className='font-display font-bold text-xl text-text-primary tracking-wide mb-0.5'>
                                {member.name}
                            </h3>
                            <p className='text-primary font-mono text-xs font-semibold uppercase tracking-wider mb-2'>
                                {member.role}
                            </p>
                            <p className='text-text-muted text-xs leading-relaxed'>
                                {member.bio}
                            </p>
                        </div>
                    </figure>


                    {/* 8 empty divs needed for the 3D effect */}
                    <div></div>
                    <div></div>
                    <div></div>
                    <div></div>
                    <div></div>
                    <div></div>
                    <div></div>
                    <div></div>
                </div>
                ))}
            </div>
    );
}