// src/components/ui/Card.jsx

import React from 'react';

export function Card({ title, subtitle, children, className = '' }) {
  return (
    <div
      className={
        [
          'bg-neutral-800/90',
          'border border-neutral-700/60',
          'rounded-xl',
          'p-4 md:p-5',
          'shadow-lg',
          'transition-all duration-200',
          'hover:-translate-y-0.5',
          'hover:shadow-xl',
          'hover:shadow-pink-500/10',
        ].join(' ') +
        ' ' +
        className
      }
    >
      {title && (
        <h3 className="text-lg font-semibold mb-1 text-white tracking-tight">
          {title}
        </h3>
      )}
      {subtitle && (
        <p className="text-sm text-neutral-400 mb-3 leading-snug">
          {subtitle}
        </p>
      )}
      <div className="text-sm text-neutral-200 space-y-1 leading-relaxed">
        {children}
      </div>
    </div>
  );
}
