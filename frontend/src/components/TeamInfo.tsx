import Image from 'next/image';
import { FaUser } from 'react-icons/fa';

interface TeamMember {
  name: string;
  role?: string;
  bio?: string;
  image_url?: string;
}

interface TeamInfoProps {
  teamMembers: TeamMember[];
}

const TeamInfo = ({ teamMembers }: TeamInfoProps) => {
  if (!teamMembers || teamMembers.length === 0) {
    return (
      <div className="text-center py-6 text-secondary-500">
        No team information available
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {teamMembers.map((member, index) => (
        <div key={index} className="card flex flex-col items-center text-center">
          <div className="w-20 h-20 rounded-full bg-gray-200 dark:bg-secondary-700 overflow-hidden mb-3 flex items-center justify-center">
            {member.image_url ? (
              <Image
                src={member.image_url}
                alt={member.name}
                width={80}
                height={80}
                className="object-cover"
              />
            ) : (
              <FaUser className="text-3xl text-gray-400 dark:text-gray-600" />
            )}
          </div>
          <h4 className="font-medium text-lg">{member.name}</h4>
          {member.role && (
            <p className="text-sm text-primary-600 dark:text-primary-400 mb-2">{member.role}</p>
          )}
          {member.bio && (
            <p className="text-sm text-secondary-600 dark:text-secondary-400 mt-2">
              {member.bio.length > 150 ? `${member.bio.substring(0, 150)}...` : member.bio}
            </p>
          )}
        </div>
      ))}
    </div>
  );
};

export default TeamInfo;
