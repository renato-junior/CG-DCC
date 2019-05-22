phong_vertex_shader = """
    #version 130

    uniform mat4 model_view_matrix;
    uniform mat4 normal_matrix;
    uniform mat4 model_view_projection_matrix;     

    out vec3 Normal;
    out vec3 Vertex;

    void main()
    {
        Vertex = vec3(model_view_matrix * gl_Vertex);
        Normal = vec3(normalize(normal_matrix * vec4(gl_Normal, 0.0)));
        gl_Position = model_view_projection_matrix * gl_Vertex;
    }

    """

phong_fragment_shader = """
    #version 130

    in vec3 Normal;
    in vec3 Vertex;

    uniform vec3 aColor;
    uniform vec3 lPosition;
    uniform vec3 lColor;
    uniform vec3 lSpecular;
    uniform float mShininess;

    void main()
    {
        vec3 L = normalize(lPosition - Vertex);
        vec3 E = normalize(-Vertex);
        vec3 R = normalize(-reflect(L, Normal));

        // Ambient
        vec4 ambient = vec4(aColor, 1.0);

        // Diffuse term
        vec4 diffuse = vec4(max(dot(L, Normal), 0) * lColor, 0.0);

        // Specular term
        vec4 specular = vec4(lSpecular * pow(max(dot(R, E), 0.0), 0.3 * mShininess), 0.0);

        gl_FragColor = ambient + diffuse + specular;
    }
    """

gouraud_vertex_shader = """
    #version 130

    uniform mat4 model_view_matrix;
    uniform mat4 normal_matrix;
    uniform mat4 model_view_projection_matrix;   
      
    uniform vec3 aColor;
    uniform vec3 lPosition;
    uniform vec3 lColor;
    uniform vec3 lSpecular;
    uniform float mShininess;

    out vec4 newColor;
    void main()
    {
        vec3 Vertex = vec3(model_view_matrix * gl_Vertex);
        vec3 Normal = vec3(normalize(normal_matrix * vec4(gl_Normal, 0.0)));
        gl_Position = model_view_projection_matrix * gl_Vertex;

        vec3 L = normalize(lPosition - Vertex);
        vec3 E = normalize(-Vertex);
        vec3 R = normalize(-reflect(L, Normal));

        vec4 ambient = vec4(aColor, 0);
        vec4 diffuse = vec4(max(dot(L, Normal), 0) * lColor, 0.0);
        vec4 specular = vec4(lSpecular * pow(max(dot(R, E), 0.0), 0.3 * mShininess), 0.0);
        
        newColor =  ambient + diffuse + specular;
    }

    """

gouraud_fragment_shader = """
    #version 130

    in vec4 newColor;

    void main()
    {
        gl_FragColor = newColor;
    }
    """

flat_vertex_shader = """
    #version 130

    uniform mat4 model_view_matrix;
    uniform mat4 model_view_projection_matrix;   

    out vec3 Vertex;
    
    void main()
    {
        Vertex = vec3(model_view_matrix * gl_Vertex);
        gl_Position = model_view_projection_matrix * gl_Vertex;
    }

    """

flat_fragment_shader = """
    #version 130

    in vec3 Vertex;

    uniform vec3 aColor;
    uniform vec3 lPosition;
    uniform vec3 lColor;
    uniform vec3 lSpecular;
    uniform float mShininess;

    void main()
    {
        vec3 Normal = normalize(cross(dFdx(Vertex), dFdy(Vertex)));

        vec3 L = normalize(lPosition - Vertex);
        vec3 E = normalize(-Vertex);
        vec3 R = normalize(-reflect(L, Normal));

        vec4 ambient = vec4(aColor, 0);
        vec4 diffuse = vec4(max(dot(L, Normal), 0) * lColor, 0.0);
        vec4 specular = vec4(lSpecular * pow(max(dot(R, E), 0.0), 0.3 * mShininess), 0.0);
        
        gl_FragColor =  ambient + diffuse + specular;
    }
    """
