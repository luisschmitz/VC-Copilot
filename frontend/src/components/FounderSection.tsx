"use client";

import { FounderResponse, FounderInfo } from '@/types/api';

interface FounderSectionProps {
  founderData: FounderResponse;
}

export default function FounderSection({ founderData }: FounderSectionProps) {
  const { founders = [], founding_story = '', company_name = '' } = founderData || {};

  return (
    <div>
      <h2 className="text-lg font-medium text-gray-900 mb-4">Founder Information</h2>
      
      {founding_story && (
        <div className="mb-6">
          <h3 className="text-md font-medium text-gray-700 mb-2">Founding Story</h3>
          <div className="bg-gray-50 p-4 rounded-md">
            <p className="text-sm text-gray-600 whitespace-pre-line">{founding_story}</p>
          </div>
        </div>
      )}

      <div className="space-y-6">
        {founders.length === 0 ? (
          <p className="text-gray-500 italic">No founder information available.</p>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            {founders.map((founder, index) => (
              <FounderCard key={index} founder={founder} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

interface FounderCardProps {
  founder: FounderInfo;
}

function FounderCard({ founder }: FounderCardProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      <div className="p-5">
        <div className="flex items-center space-x-3 mb-3">
          <div className="flex-shrink-0 h-10 w-10 bg-indigo-100 rounded-full flex items-center justify-center">
            <span className="text-indigo-600 font-medium text-lg">
              {founder.name.split(' ').map(part => part[0]).join('')}
            </span>
          </div>
          <div>
            <h3 className="text-lg font-medium text-gray-900">{founder.name}</h3>
            {founder.title && <p className="text-sm text-gray-500">{founder.title}</p>}
          </div>
        </div>

        <div className="space-y-3 text-sm">
          {founder.education && founder.education.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-700">Education</h4>
              <ul className="list-disc list-inside text-gray-600 ml-2">
                {founder.education.map((edu, idx) => (
                  <li key={idx}>
                    {edu.degree} at {edu.institution}
                    {edu.year && `, ${edu.year}`}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {founder.work_experience && founder.work_experience.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-700">Work Experience</h4>
              <ul className="list-disc list-inside text-gray-600 ml-2">
                {founder.work_experience.map((exp, idx) => (
                  <li key={idx}>
                    {exp.role} at {exp.company}, {exp.duration}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {founder.previous_startups && founder.previous_startups.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-700">Previous Startups</h4>
              <ul className="list-disc list-inside text-gray-600 ml-2">
                {founder.previous_startups.map((startup, idx) => (
                  <li key={idx}>
                    {startup.name} - {startup.outcome}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {founder.expertise && founder.expertise.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-700">Expertise</h4>
              <div className="flex flex-wrap gap-1">
                {founder.expertise.map((skill, idx) => (
                  <span key={idx} className="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {founder.social_profiles && Object.keys(founder.social_profiles).length > 0 && (
            <div>
              <h4 className="font-medium text-gray-700">Social Profiles</h4>
              <ul className="list-disc list-inside text-gray-600 ml-2">
                {Object.entries(founder.social_profiles).map(([platform, url], idx) => (
                  <li key={idx}>
                    <a href={url} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">
                      {platform.charAt(0).toUpperCase() + platform.slice(1)}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
