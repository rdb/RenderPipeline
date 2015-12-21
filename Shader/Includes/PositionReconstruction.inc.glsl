#pragma once

uniform mat4 trans_clip_of_mainCam_to_mainRender;
uniform mat4 trans_mainRender_to_view_of_mainCam;
uniform mat4 trans_mainRender_to_clip_of_mainCam;

uniform mat4 currentProjMatInv;
uniform mat4 currentProjMat;

// Constant values based on main camera near and far plane
const float NDC_NEAR = CAMERA_NEAR;
const float NDC_FAR = CAMERA_FAR;
const float NDC_A = NDC_NEAR + NDC_FAR;
const float NDC_B = NDC_NEAR - NDC_FAR;
const float NDC_C = 2.0 * NDC_NEAR * NDC_FAR;
const float NDC_D = NDC_FAR - NDC_NEAR;

// Computes the Z component from a position in NDC space
float get_z_from_ndc(vec3 ndc_pos) {
  return NDC_C / (NDC_A + (ndc_pos.z * NDC_B));
}

// Computes the Z component from a position in NDC space, with a given near and far plane
float get_z_from_ndc(vec3 ndc_pos, float near, float far) {
  return (2.0 * near * far / ((near + far) + ndc_pos.z * (near-far)));
}

// Computes the Z component from linear Z
float get_z_from_linear_z(float z) {
  return fma((1.0 / (z / NDC_C) - NDC_A) / NDC_B, 0.5, 0.5);
}

// Computes linear Z from a given Z value
float get_linear_z_from_z(float z) {
    return NDC_C / (NDC_A - fma(z, 2.0, -1.0) * NDC_D);
}

// Computes linear Z from a given Z value, and near and far plane
float get_linear_z_from_z(float z, float near, float far) {
    return 2.0 * near * far / (far + near - fma(z, 2.0, -1.0) * (far - near));
}

// Computes linear Z from a given Z value, and near and far plane, for orthographic projections
float get_linear_z_from_z_ortographic(float z, float near, float far) {
  return 2.0 / (far + near - fma(z, 2.0, -1.0) * (far - near));
}

// Converts a nonlinear Z to a linear Z from 0 .. 1
float normalize_to_linear_z(float z, float near, float far) {
  return get_linear_z_from_z(z, near, far) / far;
}

// Computes the surface position based on a given Z, a texcoord, and the Inverse MVP matrix
vec3 calculate_surface_pos(float z, vec2 tcoord, mat4 inverse_mvp) {
  vec3 ndc_pos = fma(vec3(tcoord.xy, z), vec3(2.0), vec3(-1.0));    
  float clip_w = get_z_from_ndc(ndc_pos);

  // TODO: Don't we have to do the w-divide here?
  return (inverse_mvp * vec4(ndc_pos * clip_w, clip_w)).xyz;
}

// Computes the surface position based on a given Z and a texcoord
vec3 calculate_surface_pos(float z, vec2 tcoord) {
  return calculate_surface_pos(z, tcoord, trans_clip_of_mainCam_to_mainRender);
}

// Computes the surface position based on a given Z and a texcoord, aswell as a
// custom near and far plane, and the inverse MVP. This is for orthographic projections
vec3 calculate_surface_pos_ortho(float z, vec2 tcoord, float near, float far, mat4 inverse_mvp) {
  vec3 ndc_pos = fma(vec3(tcoord.xy, z), vec3(2.0), vec3(-1.0));
  float clip_w = get_linear_z_from_z_ortographic(z, near, far);
  vec4 result = inverse_mvp * vec4(ndc_pos * clip_w, clip_w);
  return result.xyz / result.w;
}

// Computes the view position from a given Z value and texcoord
vec3 calculate_view_pos(float z, vec2 tcoord) {
  vec4 view_pos = currentProjMatInv *
    vec4(fma(tcoord.xy, vec2(2.0), vec2(-1.0)), z, 1.0);
  return view_pos.xyz / view_pos.w;
}

// Computes the NDC position from a given view position
vec3 view_to_screen(vec3 view_pos) {
  vec4 projected = currentProjMat * vec4(view_pos, 1);
  projected.xyz /= projected.w;
  projected.xy = fma(projected.xy, vec2(0.5), vec2(0.5));
  return projected.xyz;
}

// Converts a view space normal to world space
vec3 view_normal_to_world(vec3 view_normal) {
  // We need to transform the coordinate system, should not be required,
  // seems to be some panda bug?
  view_normal = view_normal.xzy * vec3(1, -1, 1);
  return normalize((vec4(view_normal, 0) * trans_mainRender_to_view_of_mainCam).xyz);
}

// Converts a world space position to screen space position (NDC)
vec3 world_to_screen(vec3 world_pos) {
  vec4 proj = trans_mainRender_to_clip_of_mainCam * vec4(world_pos, 1);
  proj.xyz /= proj.w;
  proj.xy = fma(proj.xy, vec2(0.5), vec2(0.5));
  return proj.xyz;
}

// Converts a world space normal to view space
vec3 world_normal_to_view(vec3 world_normal) {
  vec4 proj = trans_mainRender_to_view_of_mainCam * vec4(world_normal, 0);
  proj.xyz *= vec3(1, -1, 1);
  return normalize(proj.xzy);
}
